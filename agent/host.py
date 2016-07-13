import xml.etree.ElementTree as ET
from log import logger
import os, sys
import libvirt
import constants

import subprocess
import commands
import time
import urllib
import re
import urllib2


class vmmhost:
    def __init__(self, sn, conn):
        self.conn = conn
        self.sn = sn

    def get_vmlist(self):
        dom_names = []
        for dom in self.conn.listAllDomains():
            dom_names.append(dom.name())
        return dom_names

    def get_sw_info(self):
        ret = {}
        hv_ver = self.conn.getVersion()
        major = hv_ver / 1000000
        minor = hv_ver % 1000000 / 1000
        release = hv_ver % 1000
        hv_ver = str(major)+'.'+str(minor)+'.'+str(release)

        lib_ver = self.conn.getLibVersion()
        major = lib_ver / 1000000
        minor = lib_ver % 1000000 / 1000
        release = lib_ver % 1000
        lib_ver = str(major)+'.'+str(minor)+'.'+str(release)

        abspath = os.path.dirname(os.path.abspath(__file__))
        cli_ver = open(abspath + "/VERSION").readline().rstrip('\r\n')

        cmd = "uname -r"
        os_ver = commands.getoutput(cmd)
        
        ret['version'] = cli_ver
        ret['libvirt_version'] = lib_ver
        ret['hv_version'] = hv_ver
        ret['os_version'] = os_ver
        return ret
        
    def get_out_ip(self):
        response = urllib2.urlopen('http://www.ip.cn')
        html = response.read()
        ip=re.search(r'code.(.*?)..code',html)
        return ip.group(1)

    def get_hw_info(self):
        ret = {}
        cmd = "lscpu | grep '^Arch' | awk '{print $2}'"
        result = commands.getoutput(cmd)
        ret['architecture'] = result
        
        cmd = "lscpu | grep '^CPU(s)' | awk '{print $2}'"
        result = commands.getoutput(cmd)
        ret['cpus'] = int(result)

        cmd = "lscpu | grep '^Model name' | awk -F: '{print $2}'"
        result = commands.getoutput(cmd)
        ret['cpu_name'] = result.strip()
        disk_size_cmd = "lsblk -b  --output=NAME,SIZE | grep '^.d' | awk '{printf(\"%s\\n%s\\n\", $1,$2)}'"
        cmd_result = commands.getoutput(disk_size_cmd)
        disk_size = 0
        disk_num = 0
        disk_info = []
        i = 0
        #for i < len(cmd_result):
        cmd_result_list = cmd_result.splitlines()
        while i < len(cmd_result_list):
        #for item in cmd_result.splitlines():
            disk_item = {}
            disk_item['name'] = cmd_result_list[i]
            i += 1
            disk_item['size'] = cmd_result_list[i]
            i += 1
            disk_info.append(disk_item)
            disk_size += int(disk_item['size'])
            disk_num += 1
        ret['disk'] = disk_info
        ret['disk_size'] = disk_size 
        ret['data_disk_num'] = disk_num
        
        nodeinfo = self.conn.getInfo()
        '''
        print('Model: '+str(nodeinfo[0]))
        print('Memory size: '+str(nodeinfo[1])+'MB')
        print('Number of CPUs: '+str(nodeinfo[2]))
        print('MHz of CPUs: '+str(nodeinfo[3]))
        print('Number of NUMA nodes: '+str(nodeinfo[4]))
        print('Number of CPU sockets: '+str(nodeinfo[5]))
        print('Number of CPU cores per socket: '+str(nodeinfo[6]))
        print('Number of CPU threads per core: '+str(nodeinfo[7]))
        '''
        ret['total_mem'] = int(nodeinfo[1])*1024*1024

        return ret 

    def get_memory_usage(self):
        """
        Function return memory usage on node.
        """
        get_all_mem = self.conn.getInfo()[1] * 1048576
        get_freemem = self.conn.getMemoryStats(-1, 0)
        print get_freemem
        if type(get_freemem) == dict:
            free = (get_freemem.values()[0] +
                    get_freemem.values()[2] +
                    get_freemem.values()[3]) * 1024
            percent = ("%2.f" % (100 - ((free * 100 * 1.0) / get_all_mem)))
            usage = (get_all_mem - free)
            mem_usage = {
                        'mem_all': get_all_mem, 
                        'mem_free': free, 
                        'mem_usage': percent
                        }
        else:
            mem_usage = None

        return mem_usage

    def get_cpu_usage(self):
        """
        Function return cpu usage on node.
        """
        prev_idle = 0
        prev_total = 0
        cpu = self.conn.getCPUStats(-1, 0)
        if type(cpu) == dict:
            for num in range(2):
                idle = self.conn.getCPUStats(-1, 0).values()[1]
                total = sum(self.conn.getCPUStats(-1, 0).values())
                diff_idle = idle - prev_idle
                diff_total = total - prev_total
                diff_usage = ("%.2f" % ((1000 * (diff_total - diff_idle) * 1.0 / diff_total + 5) / 10))
                prev_total = total
                prev_idle = idle
                if num == 0:
                    time.sleep(1)
                else:
                    if diff_usage < 0:
                        diff_usage = 0
        else:
            return None
        return {'cpu_usage': diff_usage}

    def get_rx_tx(self, itface):
        try:
            cmd_rx = "cat /sys/class/net/%s/statistics/rx_bytes" % itface
            cmd_tx = "cat /sys/class/net/%s/statistics/tx_bytes" % itface
            data_rx_prev = commands.getoutput(cmd_rx)
            data_tx_prev = commands.getoutput(cmd_tx)
    
            time.sleep(1)
            data_rx_now = commands.getoutput(cmd_rx)
            data_tx_now = commands.getoutput(cmd_tx)
    
            rx = (float(data_rx_now) - float(data_rx_prev))/1024
            rx = ("%.2f" % rx)
            tx = (float(data_tx_now) - float(data_tx_prev))/1024
            tx = ("%.2f" % tx)

        except Exception, e:
            logger.exception(e)
            return None

        return {"in" : rx, "out" : tx}
        

    def get_net_usage(self, itfaces = ["ovirtmgmt"]):
        ret = []

        for itface in itfaces:
            item = {}
            item['name'] = itface
            item['type'] = 'service'
            rx_tx = self.get_rx_tx(itface)
            if rx_tx is not None:
                item['in'] = rx_tx['in']
                item['out'] = rx_tx['out']

            ret.append(item)
        return ret
        
    def get_disk_usage(self):
        """
        Function return cpu usage on node.
        """
        ret_list = []
        cmd = "df -l | grep -v ^Filesystem "
        result = commands.getoutput(cmd)
        for item in result.splitlines():
            ret_list.append({})    

        col = ("source", "size", "avail", "pcent", "target")
        for item_col in col:
            i = 0
            cmd = "df -l --output=%s | awk 'NR>1 {print $0}'" % item_col
            result = commands.getoutput(cmd)
            for item in result.splitlines():
                ret_list[i][item_col] = item.strip()
                i += 1

        logger.debug(ret_list)
        #delete tmpfs: delete the one that does not begin with '/'
        for index in range(len(ret_list)-1, -1, -1):
            if re.match('/', ret_list[index]["source"]) is None:
                del(ret_list[index])
            else:
                #add column: util
                cmd = "iostat -x %s | grep  -A1 util | tail -1 | awk '{print $NF}' " % ret_list[index]["source"]
                result = commands.getoutput(cmd)
                ret_list[index]['util'] = float(result)*100
                #delete character '%'
                ret_list[index]['pcent'] = ("%.2f" % float(ret_list[index]['pcent'][:-1]))
            
        return ret_list

    def get_hostname(self):
        return self.conn.getHostname()

    def get_resource_info(self):
        pass

    @staticmethod
    def get_file_list(path):
        ret_list = []
        files = os.listdir(path)
        for fi in files:
            if os.path.isfile(os.path.join(path, fi)):
                ret_list.append(fi)

        return ret_list
    
    def download_res(self, url, checksum, save_to_path):
        i = 1
        percent = 0
        def report(count, blockSize, totalSize):
            percent = int(count*blockSize*100/totalSize)
            sys.stdout.write("\r  %d   %d   %d%%" % (i, count, percent) + ' complete')
            sys.stdout.flush()
        filename = commands.getoutput('basename %s' % url)
        print '1111'
        urllib.urlretrieve(url, save_to_path + '/' + filename, reporthook=report)
        print '22222'
        pass

    @staticmethod
    def report(count, blockSize, totalSize):
        percent = int(count*blockSize*100/totalSize)
        sys.stdout.write("\r %d   %d%%" % (count, percent) + ' complete')
        sys.stdout.flush()
