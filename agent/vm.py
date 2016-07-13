import xml.etree.ElementTree as ET
from log import logger
import os, sys
import time
import libvirt
from xml_api import hd_xml, cdrom_xml, extract_harddisk_labels,construct_snapshot_xml
import constants
import commands
import json
import re
import base64

"""
def report_libvirt_error():
    err = libvirt.virGetLastError()
    print(libvirt.libvirtError("").get_error_message())
"""

storage_path = "/home/louzhengwei/test/sdb2/"
testxml="""
<domain type='kvm'>
  <name>clone1</name>
  <memory unit='KiB'>2097152</memory>
  <currentMemory unit='KiB'>2097152</currentMemory>
  <vcpu placement='static' current='1'>16</vcpu>
  <cputune>
    <shares>1020</shares>
  </cputune>
  <sysinfo type='smbios'>
    <system>
      <entry name='manufacturer'>oVirt</entry>
      <entry name='product'>oVirt Node</entry>
      <entry name='version'>7-1.1503.el7.centos.2.8</entry>
      <!--entry name='serial'>4C4C4544-0046-5A10-8052-B9C04F533258</entry-->
    </system>
  </sysinfo>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.2.0'>hvm</type>
    <smbios mode='sysinfo'/>
  </os>
  <features>
    <acpi/>
  </features>
  <cpu mode='custom' match='exact'>
    <model fallback='allow'>Nehalem</model>
    <topology sockets='16' cores='1' threads='1'/>
    <numa>
      <cell id='0' cpus='0' memory='2097152' unit='KiB'/>
    </numa>
  </cpu>
  <clock offset='variable' adjustment='0' basis='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <controller type='usb' index='0'>
      <alias name='usb'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'>
      <alias name='pci.0'/>
    </controller>
    <controller type='ide' index='0'>
      <alias name='ide'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <controller type='virtio-serial' index='0'>
      <alias name='virtio-serial0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </controller>
    <interface type='bridge'>
      <source bridge='ovirtmgmt'/>
      <target dev='vnet0'/>
      <model type='virtio'/>
      <link state='up'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <channel type='unix'>
      <source mode='bind' path='/var/lib/libvirt/qemu/channels/4fa9bcdf-7ae8-4dd1-aa29-bf98acf14a35.com.redhat.rhevm.vdsm'/>
      <target type='virtio' name='com.redhat.rhevm.vdsm' state='disconnected'/>
      <alias name='channel0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <channel type='unix'>
      <source mode='bind' path='/var/lib/libvirt/qemu/channels/4fa9bcdf-7ae8-4dd1-aa29-bf98acf14a35.org.qemu.guest_agent.0'/>
      <target type='virtio' name='org.qemu.guest_agent.0' state='disconnected'/>
      <alias name='channel1'/>
      <address type='virtio-serial' controller='0' bus='0' port='2'/>
    </channel>
    <input type='tablet' bus='usb'>
      <alias name='input0'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='5900' autoport='yes' listen='192.168.1.27' passwdValidTo='2016-04-27T05:39:22'>
      <listen type='network' address='192.168.1.27' network='vdsm-ovirtmgmt'/>
    </graphics>
    <video>
      <model type='cirrus' vram='1638' heads='1'/>
      <alias name='video0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='none'/>
  </devices>
  <seclabel type='dynamic' model='selinux' relabel='yes'>
    <label>system_u:system_r:svirt_t:s0:c170,c830</label>
    <imagelabel>system_u:object_r:svirt_image_t:s0:c170,c830</imagelabel>
  </seclabel>
</domain>

"""

level_testxml="""
<domlevel>
    <disk type='file' size='2'/>
    <disk type='block' size='3'/>
</domlevel>
"""

class vm:
    def __init__(self, name = "", uri = "qemu:///system"):
        self.name = name
        self.id = ""
        self.xml = ""  #don't modify it 
        self.temp = {
                    'total_cpu_time': 0L,
                    'last_cpu_idle_time': 0L,
                    'disk_read_request': 0L,
                    'disk_write_request': 0L,
                    'disk_read': 0L,
                    'disk_write': 0L,
                    'disk_read_delay': 0,
                    'disk_write_delay': 0,
                    'network_receive_bytes': 0L,
                    'network_transfer_bytes': 0L,
                    'disk_partition_info': {},
                    'timestamp': 0L
                }
        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(name)
            self.xml = dom.XMLDesc()
            conn.close()
        except Exception, e:
            logger.exception(e)

    def get_domain(self, uri="qemu:///system"):
        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            return dom
            conn.close()
        except Exception, e:
            logger.exception(e)
            return None

    def get_mem(self):
        tree = ET.fromstring(self.xml)
        size = tree.find('currentMemory').text
        return int(size)*1024

    def get_cpu_num(self):
        ret = 0
        tree = ET.fromstring(self.xml)
        vcpu_ele = tree.find('vcpu')
        max_vcpu = vcpu_ele.text
        current_vcpu = vcpu_ele.get('current')
        if ( current_vcpu is not None):
            ret = int(current_vcpu)
        ret = int(max_vcpu)
        return ret

    def get_disk_info(self):
        ret = []
        tree = ET.fromstring(self.xml)
        for item in tree.findall('devices/disk'):
            path = None
            driver_type = item.find('driver').get('type')
            target = item.find('target').get('dev')
            bus = item.find('target').get('bus')
            disk_type = item.get('type')
            if (disk_type == "file"):
                path = item.find('source').get('file')
            elif (disk_type == "block"):
                path = item.find('source').get('dev')
            else:
                logger.warning("invalid disk_type: %s" % disk_type)
            print('path: %s' % path)

            #attention: filename and size should be initilize if path is None
            if path  is not None:
                filename = os.path.basename(path)
                cmd = "qemu-img info " + path + " | grep 'virtual size'  | awk -F'(' '{print $2}' | awk '{print $1}' "
                status, output = commands.getstatusoutput(cmd)
                if status == 0:
                    try:
                        size = int(output)
                    except Exception, e:
                        logger.error("%s: faild"%cmd)
                        size = 0
                else:
                    size = 0
                    logger.error("%s: faild"%cmd)
            else:
                path = ""
                filename = ""
                size = 0
            
            item_dict = {}
            item_dict['name'] = filename
            item_dict['size'] = size
            item_dict['path'] = path
            item_dict['format'] = driver_type
            item_dict['bus'] = bus
            item_dict['target'] = target

            logger.debug(item_dict)
            ret.append(item_dict)

        logger.debug(json.dumps(ret))

        return ret
        
    def get_net_info(self):
        ###{ name: "eth0", link_way: "bridge",  linked:0, select: "eth0"}
        ret = []
        tree = ET.fromstring(self.xml)
        for item in tree.findall('devices/interface'):
            itface = item.get('type')
            if (itface != "bridge"):
                logger.warning("invalid network interface type: %s" % itface)
                continue

            src_name = item.find('source').get('bridge')
            
            item_dict = {}
            item_dict['name'] = src_name 
            item_dict['link_way'] = itface
            item_dict['linked'] = 1    #todo
            item_dict['select'] = "ovirtmgmt"   #todo 

            ret.append(item_dict)

        logger.debug(json.dumps(ret))
        return ret

    def get_snapshots(self):
        ret = self.get_domain().snapshotListNames()
        return ret
        pass

    def change_boot_type(self, boot_type):
        tree = ET.fromstring(self.xml)
        tree.find('os/boot').set('dev', boot_type)
        self.xml = ET.tostring(tree)
        return self.xml
        
    def change_memory(self, size):
        tree = ET.fromstring(self.xml)
        tree.find('memory').text = str(size)
        tree.find('currentMemory').text = str(size)
        self.xml = ET.tostring(tree)
        return self.xml

    def change_cur_cpu_number(self, number, uri="qemu:///system"):
        try:
            conn = libvirt.open(uri)
            nodeinfo = conn.getInfo()
        except Exception, e:
            logger.exception(e)
            return None 
        if conn:
            conn.close()

        host_maxcpus = int(nodeinfo[2])
        if number > host_maxcpus or number <= 0:
            logger.warning("invalid cpu number")
            return None

        tree = ET.fromstring(self.xml)
        vcpu_ele = tree.find('vcpu')
        max_vcpu = vcpu_ele.text
        if max_vcpu is not None and int(max_vcpu) < number:
            vcpu_ele.text = str(number)
        vcpu_ele.set('current', str(number))

        topo_ele = tree.find('cpu/topology')
        if topo_ele:
            topo_ele.set('sockets', vcpu_ele.text)
            topo_ele.set('cores', '1')
            topo_ele.set('threads', '1')
        self.xml = ET.tostring(tree)
        return self.xml

    @staticmethod
    def prepare_img(task_item):
        vm_name = task_item.data['vm_name']
        os_size = (task_item.data['disk_os'] /512+1)*512   #size must be a multiple of 512
        data_size = task_item.data['disk_data']
        install_method = task_item.data['install_method']
        vm_file = task_item.data['vm_file']
        ret_data_disk = []

        os_path = constants.img_os_path + '/' + vm_name + '_os.qcow2'

        #create os disk
        if install_method == 0:
            #iso
            os_cmd = 'qemu-img create -f qcow2 %s %d > /dev/null 2>&1' % (os_path, os_size)
            logger.debug(os_cmd)
            
        elif install_method == 1:
            #img
            template_path = constants.img_template_path + '/' + os.path.basename(vm_file)
            os_cmd = '\cp -f %s %s' % (template_path, os_path)
            logger.debug(os_cmd)
        else:
            return None

        stat = os.system(os_cmd)
        if stat != 0:
            logger.error("%s: faild" % os_cmd)

        chmod_cmd = 'chmod 777 %s' % os_path
        stat = os.system(chmod_cmd)
        if stat != 0:
            logger.error("%s: faild" % os_cmd)

        #create data disk
        data_disk_list = []
        for i in os.listdir(constants.img_root_path):
            if re.match('^data[0-9]*$', i) is None:
                continue
            data_disk_path = os.path.join(constants.img_root_path ,i)
            if os.path.isdir(data_disk_path):
                data_disk_list.append(data_disk_path)
        data_disk_list.sort()
        single_data_size = int(data_size) / len(data_disk_list)
        single_data_size = (single_data_size/512+1)*512  #size must be a multiple of 512

        index = 0
        for item in data_disk_list:
            index += 1
            data_abs_path = item + '/' + vm_name + '_' + str(index) + '.qcow2'
            data_cmd = 'qemu-img create -f qcow2 %s %d > /dev/null 2>&1' % (data_abs_path, single_data_size) 
            stat = os.system(data_cmd)
            logger.debug(data_cmd)
            if stat != 0:
                logger.error("%s: faild" % data_cmd)
                return None
            chmod_cmd = 'chmod 777 %s' % data_abs_path
            stat = os.system(chmod_cmd)
            if stat != 0:
                logger.error("%s: faild" % os_cmd)
                return None
            ret_data_disk.append(data_abs_path)

        return os_path,ret_data_disk

    def delete_img(self):
        tree = ET.fromstring(self.xml)
        for sources in tree.findall('devices/disk/source'):
            file_path = sources.get("file")
            if file_path is None:
                continue
            if re.match(constants.img_os_path, file_path) is not None or re.match(constants.img_data_path.rstrip('/'), file_path) is not None:
                cmd = "rm -f %s" % file_path
                stat = os.system(cmd)
                if stat != 0:
                    logger.error("%s: faild" % cmd)
                    #don't need to handle delete exception
        
    def extend_img(self, task_item):
        sysdisk_extend = task_item.data['sysdisk_extend']
        datadisk_extend = task_item.data['datadisk_extend']

        os_path = ""
        data_path_list = []
        tree = ET.fromstring(self.xml)
        for sources in tree.findall('devices/disk/source'):
            file_path = sources.get("file")
            if file_path is None:
                continue
            if re.match(constants.img_os_path, file_path) is not None:
                os_path = file_path
            elif re.match(constants.img_data_path.rstrip('/'), file_path) is not None:
                data_path_list.append(file_path)
            else:
                continue
        sysdisk_extend = (sysdisk_extend/512+1)*512
        if int(sysdisk_extend) > 0 and os_path != "":
            os_cmd = 'qemu-img resize %s +%d' % (os_path, sysdisk_extend)
            logger.debug(os_cmd)
            stat = os.system(os_cmd)
            if stat != 0:
                logger.error("%s: faild" % os_cmd)
                return False 

        data_num = len(data_path_list)
        if int(datadisk_extend) > 0 and data_num > 0:
            single_data_size = int(datadisk_extend) / data_num / 512 * 512 #size must be a multiple of 512
            for datadisk_path in data_path_list:
                data_cmd = 'qemu-img resize %s +%d' % (datadisk_path, single_data_size)
                logger.debug(data_cmd)
                stat = os.system(data_cmd)
                if stat != 0:
                    logger.error("%s: faild" % data_cmd)
                    return False
        return True

    @staticmethod
    def define(name,  xml, uri="qemu:///system"):
        conn = None
        ret={}

        try:
            conn = libvirt.open(uri)
            dom = conn.defineXML(xml)

            ret["status_code"] = 0 
            ret["msg"] = "OK"
        except Exception, e:
            logger.exception(e)
            ret["status_code"] = -1
            ret["msg"] = str(e)

        if conn:
            conn.close()

        logger.debug(ret)

        return ret

    def undefine(self, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            dom.undefine()
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

         
    def start(self, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            if dom == None:
                status_code = -1
                msg = "undefine faild: vm(%d) is not existed" % self.name
                logger.warn(msg)
            else:
                dom.create()
                status_code = 0
                msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def start_from_cdrom(self, uri, name, cdrom_name):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(name)

            old_xml = self.xml = dom.XMLDesc()
            new_xml = self.change_boot_type("cdrom")
            root_tree = ET.fromstring(new_xml)

            c_cdrom_xml = cdrom_xml('file', constants.iso_path, 21) #fixed position: 21
            if c_cdrom_xml is not None:
                root_tree.find('devices').append(c_cdrom_xml.tree)

            new_xml = ET.tostring(root_tree)
            logger.debug("new_xml: \n%s" % new_xml)
            logger.debug("old_xml: \n%s" % old_xml)

            new_dom = conn.defineXML(new_xml)
            new_dom.create()

            old_dom = conn.defineXML(old_xml)

            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def shutdown(self, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            dom.shutdown()
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def destroy(self, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            dom.destroy()
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def get_status(self, uri="qemu:///system"):
        conn = None
        ret={}
        vm_status = 0
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            status = dom.state()
            vm_status = int(status[0])
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["vm_status"] = vm_status
        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def _get_memory_usage_dict(self):
        '''
            Get memory info(MB) from /proc/meminfo.
            @return: {'total_memory': 1, 'free_memory': 1,
                      'used_memory': 1, 'memory_usage_rate': 45}
            free_memory = MemFree + Buffers + Cached
            used_memory = MemTotal - free_memory
            memory_usage_rate = used_memory * 100 / MemTotal
        '''
        mem_usage = {
            'total_memory': 0,
            'free_memory': 0,
            'used_memory': 0,
            'mem_usage': 0
        }
        mem_file_read = self.read_vm_file('/proc/meminfo')
        if mem_file_read:
            mem_info_lines = mem_file_read.splitlines()
        else:
            logger.error("read_vm_file (/proc/meminfo) failed")
            return mem_usage

        mem_usage['total_memory'] = long(mem_info_lines[0].split()[1]) / 1024
        mem_usage['free_memory'] = (long(mem_info_lines[1].split()[1])
                       + long(mem_info_lines[2].split()[1])
                       + long(mem_info_lines[3].split()[1])) / 1024
        mem_usage['used_memory'] = (mem_usage['total_memory'] -
                                    mem_usage['free_memory'])
        mem_usage['mem_usage'] = ((mem_usage['used_memory'] * 100) /
                                            mem_usage['total_memory'])

        return mem_usage

    def get_info(self, uri = "qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            dom = conn.lookupByName(self.name)
            info = cpu_info = dom.getCPUStats(True)
            #mem_info = dom.memoryStats()
            mem_info = self._get_memory_usage_dict()

            tree = ET.fromstring(dom.XMLDesc())
            iface = tree.find('devices/interface/target').get('dev')
            net_info = dom.interfaceStats(iface)

            disk_info2 = self.disk_usage(dom)
            print disk_info2
            cpu_info2 = self.cpu_usage(dom)
            print cpu_info2

            #disk_info = dom.blockStats('/home/louzhengwei/img/cds_data.qcow2')
            #info = dom.getCPUStats(True)
            print "----cccc"
            print info

            print "----bbbb"
            print "----"
            print net_info
            print "----"
            #print disk_info


            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        print '----------------'
        print cpu_info
        print '---aaaaaaaaaaa'
        ret["cpu_idle"] = ("%.2f" % (100 - float(cpu_info2['cpu'])))
        #ret["mem_usage"] = ("%.2f" % (mem_info['rss'] * 1000 * 100.0 / self.get_mem()))
        ret['mem_usage'] = ("%.2f" % mem_info['mem_usage'])

        logger.debug(ret)

        return ret

    

    def cpu_usage(self, dom):
        cpu_usage = {}
        nbcore = dom.info()[2]
        cpu_use_ago = dom.info()[4]
        print cpu_use_ago
        time.sleep(1)
        cpu_use_now = dom.info()[4]
        print cpu_use_now
        diff_usage = cpu_use_now - cpu_use_ago
        cpu_usage['cpu'] = 100 * diff_usage / (1 * nbcore * 10 ** 9L)
        return cpu_usage

    def disk_usage(self, dom):
        devices = []
        dev_usage = []
        tree = ET.fromstring(dom.XMLDesc())
        for disk in tree.findall('devices/disk'):
            if disk.get('device') == 'disk':
                dev_file = None
                dev_bus = None
                network_disk = True
                for elm in disk:
                    if elm.tag == 'source':
                        if elm.get('protocol'):
                            dev_file = elm.get('protocol')
                            network_disk = True
                        if elm.get('file'):
                            dev_file = elm.get('file')
                        if elm.get('dev'):
                            dev_file = elm.get('dev')
                    if elm.tag == 'target':
                        dev_bus = elm.get('dev')
                if (dev_file and dev_bus) is not None:
                    if network_disk:
                        dev_file = dev_bus
                    devices.append([dev_file, dev_bus])
        for dev in devices:
            rd_use_ago = dom.blockStats(dev[0])[1]
            wr_use_ago = dom.blockStats(dev[0])[3]
            time.sleep(1)
            rd_use_now = dom.blockStats(dev[0])[1]
            wr_use_now = dom.blockStats(dev[0])[3]
            rd_diff_usage = rd_use_now - rd_use_ago
            wr_diff_usage = wr_use_now - wr_use_ago
            dev_usage.append({'dev': dev[1], 'rd': rd_diff_usage, 'wr': wr_diff_usage})
        return dev_usage


    def net_usage(self, dom):
        devices = []
        dev_usage = []
        tree = ET.fromstring(dom.XMLDesc())
        for target in tree.findall("devices/interface/target"):
            devices.append(target.get("dev"))
        for i, dev in enumerate(devices):
            rx_use_ago = dom.interfaceStats(dev)[0]
            tx_use_ago = dom.interfaceStats(dev)[4]
            time.sleep(1)
            rx_use_now = dom.interfaceStats(dev)[0]
            tx_use_now = dom.interfaceStats(dev)[4]
            rx_diff_usage = (rx_use_now - rx_use_ago) * 8
            tx_diff_usage = (tx_use_now - tx_use_ago) * 8
            dev_usage.append({'dev': i, 'rx': rx_diff_usage, 'tx': tx_diff_usage})
        return dev_usage

    def edit_conf(self, new_xml, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            conn = libvirt.open(uri)
            conn.defineXML(new_xml)
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        if conn:
            conn.close()

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def create_snapshot(self, snapshot_name, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            disk_list = extract_harddisk_labels(self.xml)
            tree = construct_snapshot_xml(snapshot_name, disk_list)
            self.get_domain().snapshotCreateXML(ET.tostring(tree))
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def delete_snapshot(self, snapshot_name, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            snapshot_obj = self.get_domain().snapshotLookupByName(snapshot_name)
            snapshot_obj.delete()
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def restore_snapshot(self, snapshot_name, uri="qemu:///system"):
        conn = None
        ret={}
        status_code = 0
        msg = "OK"

        try:
            snapshot_obj = self.get_domain().snapshotLookupByName(snapshot_name)
            self.get_domain().revertToSnapshot(snapshot_obj)
            status_code = 0
            msg = "OK"
        except Exception, e:
            status_code = -1
            msg = e
            logger.exception(e)

        ret["status_code"] = status_code
        ret["msg"] = str(msg)
        logger.debug(ret)

        return ret

    def clone(self, uri, name, xml):
        pass

    def read_vm_file(self, path, uri="qemu:///system"):
        FILE_OPEN_READ="""{"execute":"guest-file-open", "arguments":{"path":"%s","mode":"r"}}"""
        FILE_READ="""{"execute":"guest-file-read", "arguments":{"handle":%s,"count":%d}}"""
        FILE_CLOSE="""{"execute":"guest-file-close", "arguments":{"handle":%s}}"""

        file_handle=-1
        try:
            file_handle=self.EXE(FILE_OPEN_READ % path)["return"]
            file_content=self.EXE(FILE_READ % (file_handle,1024000))["return"]["buf-b64"]
            file_content = base64.standard_b64decode(file_content)
        except Exception,e:
            logger.exception(e)
            return None
        finally:
            self.EXE(FILE_CLOSE % file_handle)
        return file_content
    
    def write_vm_file(self, path, content, uri="qemu:///system"):
        FILE_OPEN_WRITE="""{"execute":"guest-file-open", "arguments":{"path":"%s","mode":"w+"}}"""
        FILE_WRITE="""{"execute":"guest-file-write", "arguments":{"handle":%s,"buf-b64":"%s"}}"""
        FILE_CLOSE="""{"execute":"guest-file-close", "arguments":{"handle":%s}}"""  
        FILE_FLUSH="""{"execute":"guest-file-flush", "arguments":{"handle":%s}}"""  
        file_handle=-1
        enc_content = base64.standard_b64encode(content)
        try:
            file_handle=self.EXE(FILE_OPEN_WRITE % path)["return"]
            write_count=self.EXE(FILE_WRITE % (file_handle,enc_content))["return"]["count"]
            logger.debug("content:\n%s\npath:\n%s"%(content, path))
        except Exception,ex:
            print Exception,":",ex
            return -1
        finally:
            self.EXE(FILE_FLUSH % file_handle)
            self.EXE(FILE_CLOSE % file_handle)
        return write_count
    
    def EXE(self, param):
        cmd="""virsh qemu-agent-command %s '%s' """ % (self.name, param)
        #print "Exe command:%s" % cmd
        stream=os.popen(cmd).read()
        #todo: judge stream is json or not
        if stream is None or stream == "\n":
            return None
        else:
            return json.loads(stream)

    def _get_network_interfaces(self):
        cmd = """{ "execute": "guest-network-get-interfaces" }"""
        try:
            ifacs = self.EXE(cmd)["return"]
            print ifacs
            flow_rate_list = self._get_network_flow_rate_dict()
            for index in range(len(flow_rate_list)):
                for index_ifaces in range(len(ifacs)):
                    if flow_rate_list[index]['name'] == ifacs[index_ifaces]['name']:
                        #only suppoort ipv4
                        print '11111111111111111111111111111111'
                        print ifacs[index_ifaces]
                        print '11111111111111111111111111111111'
                        flow_rate_list[index]['mac'] = ifacs[index_ifaces]['hardware-address']
                        if ifacs[index_ifaces].has_key('ip-addresses'):
                            for item in ifacs[index_ifaces]['ip-addresses']:
                                if item['ip-address-type'] == "ipv4":
                                    ipv4 = item['ip-address']
                                    flow_rate_list[index]['ip'] = ipv4 
                                break
                        break
            logger.debug(flow_rate_list)
            return flow_rate_list 
        except Exception,ex:
            logger.exception(ex)
            return []

    def _get_network_flow_data(self):
        '''
            Get network flow datas(Byte) from network card by
            command 'ifconfig'.
            Split the grep result and divide it into list.
            @return: ['10.120.0.1', '123', '123']
        '''
        receive_bytes = 0L
        transfer_bytes = 0L
        ret = []
        # TODO(hzyangtk): When VM has multiple network card, it should monitor
        #                 all the cards but not only eth0.
        try:
            net_devs = self.read_vm_file('/proc/net/dev')
            if net_devs:
                network_lines = net_devs.splitlines()
            else:
                return []
        except Exception,e:
            logger.exception(e)
            return []
        for network_line in network_lines:
            network_datas = network_line.replace(':', ' ').split()
            try:
                if True:
                    item = {}
                    item['name'] = network_datas[0]
                    item['receive_bytes'] =  long(network_datas[1])
                    item['transfer_bytes'] = long(network_datas[9])
                    ret.append(item)
            except (KeyError, ValueError, IndexError, TypeError) as e:
                continue
        return ret

    def _get_network_flow_rate_dict(self):
        try:
            eclipse_time = 1
            old_ret = self._get_network_flow_data()
            time.sleep(eclipse_time)
            new_ret = self._get_network_flow_data()
            if len(old_ret) != len(new_ret):
                logger.warning("net interface's num is changing")
                return []

            ret = []
            for index in range(len(old_ret)):
                old_receive_bytes = old_ret[index]['receive_bytes']
                old_transfer_bytes = old_ret[index]['transfer_bytes']
                new_receive_bytes = new_ret[index]['receive_bytes']
                new_transfer_bytes = new_ret[index]['transfer_bytes']
                receive_rate = (float(new_receive_bytes - old_receive_bytes)
                                    / 1024.0 / eclipse_time)
                transfer_rate = (float(new_transfer_bytes - old_transfer_bytes)
                                    / 1024.0 / eclipse_time)
                if receive_rate < 0 or transfer_rate < 0:
                    receive_rate = 0
                    transfer_rate = 0

                item = {}
                item['name'] = old_ret[index]['name']
                item['in'] = receive_rate
                item['out'] = transfer_rate
                item['type'] = "service" #todo
                ret.append(item)
            logger.debug(ret)
            return ret

        except Exception, e:
            logger.exception(e)
            return []

    def get_os_version(self):

        value = ""
        version = self.read_vm_file('/proc/version')
        if version:
            version_lines = version.splitlines()
            value = version_lines[0].split()[2]
        else:
            logger.error("read_vm_file (/proc/version) failed")
            value = ""

        return value


