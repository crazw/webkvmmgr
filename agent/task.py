from log import logger
import constants
from xml_api import construct_vm_xml
from vm import vm
from xml_api import hd_xml
from xml_api import cdrom_xml

import threading
import threadpool
import time
import xml.etree.ElementTree as ET
import commands
import os
import urllib
import requests
import json
import traceback

data_test = [
{    "create_time": "2017-01-01 00:00:00",     "id":10,    "age": 3600,
    "type": 40,    "vm_name": "xingyu",    "formula": "",    "topology" : { "cpu" : 1, "disk" : 1},
    "cpu_num":2,
    "memory":512000000,
    "disk_os":30000000,
    "disk_data":1000000000,
    "install_method": 0,
    "vm_file": "/home/iso/centos6.7-for-xingyu.iso",
    "father_id": 1,
    "uri":"http://download.microsoft.com/download/B/8/9/B898E46E-CBAE-4045-A8E2-2D33DD36F3C4/vs2015.pro_chs.iso",
    "save_path":"/home/",
    "md5": "111",


},

{    "create_time": "2017-01-01 00:00:00",     "id":11,    "age": 3600,
    "type": 1,    "vm_name": "xingyu",    "formula": "",    "topology" : { "cpu" : 1, "disk" : 1},
    "cpu_num":2,
    "memory":512000000,
    "disk_os":30,
    "disk_data":100,
    "install_method": 1,
    "vm_file": "/home/iso/centos6.7-for-xingyu.iso",
    "father_id": 1,
    "uri":"http://111.1.50.20/files/41110000000A2446/download.microsoft.com/download/5/c/1/5c156922-ca10-49d8-b7e7-9bf092c3b6eb/VS2010ExpressCHS.iso",
    "save_path":"/home/",
    "md5": "111",


},
{    "create_time": "2017-01-01 00:00:00",     "id":12,    "age": 3600,
    "type": 40,    "vm_name": "xingyu",    "formula": "",    "topology" : { "cpu" : 1, "disk" : 1},
    "cpu_num":2,
    "memory":512000000,
    "disk_os":30,
    "disk_data":100,
    "install_method": 1,
    "vm_file": "/home/iso/centos6.7-for-xingyu.iso",
    "father_id": 1,
    "uri":"http://111.1.50.20/files/41110000000A2446/download.microsoft.com/download/5/c/1/5c156922-ca10-49d8-b7e7-9bf092c3b6eb/VS2010ExpressCHS.iso",
    "save_path":"/home/",
    "md5": "111",


}
]


class task:
    def __init__(self, task_item_dict):
        self.id = task_item_dict['id']
        self.create_time = task_item_dict['create_time']
        self.age = task_item_dict['age']
        self.type = task_item_dict['type']
        self.data = task_item_dict

        self.status = 0 #0: receive
        self.rev_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #now 
        self.msg = ""
        self.percent = 0
        self.consuming = 0
        self.begin_handle_time = 0

    def expired_time(self):
        return time.mktime(time.strptime(self.create_time, "%Y-%m-%d %H:%M:%S")) + self.age
        
    def is_expired(self):
        logger.debug("")
        if time.time() <= self.expired_time():
            logger.debug("")
            return False
        else:
            logger.debug("")
            return True
        



class task_manager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.unfinished_task_dict = {}
        self.finished_task_dict = {}
        self.unfinished_task_lock = threading.Lock()
        self.finished_task_lock = threading.Lock()

        self.pool = threadpool.ThreadPool(5)
        self.task_handle_funcs = {
            1 : self.task_define,
            2 : self.task_modify,
            3 : self.task_delete,
            4 : self.task_create_snapshot,
            5 : self.task_restore_snapshot,
            6 : self.task_clone,
            7 : self.task_delete_snapshot,
            8 : self.task_set_ip,
            20 : self.task_action,
            40 : self.task_download
        }

        pass
    

    def run(self):
        sn = 'CAS1000000000'
        url_task = constants.url_task +sn + '/'
        #data = data_test
        data = []
        #self.task_dispatch(data)
        while 1:
            try:
                r = requests.post(url_task)
                logger.debug(r.text)
                data = r.text
                logger.debug('--------------begin: get tasks from url----------------')
                logger.debug(data)
                json_data = json.loads(data)
                logger.debug('--------------end: get tasks from url----------------')
                #data = data_test
                self.task_dispatch(json_data['body'])

                time.sleep(2)
                self.task_status_report()
            except Exception, e:
                logger.exception(e)

            time.sleep(5)
        pass

    def task_dispatch(self, task_list):
        current_task_list = []
        print task_list
        for item in task_list:
            print item
            print "111111111111111111111"
            task_item = task(item)
            current_task_list.append(task_item)

            self.unfinished_task_lock.acquire()
            self.unfinished_task_dict[task_item.id] = task_item
            self.unfinished_task_lock.release()

        logger.debug(current_task_list)
        requests = threadpool.makeRequests(self.task_handling, current_task_list, self.task_done_print)
        [self.pool.putRequest(req) for req in requests]
        
    def task_is_expired(self, task_item):
        logger.debug("")
        return task_item.is_expired()

    def task_handling(self, task_item):
        logger.debug(task_item.id)
        self.begin_handle_time = time.time()
        if self.task_is_expired(task_item):
            logger.debug("##################### expired")
            self.invalid_task_done(task_item, constants.ERROR_MSG_EXPIRED)
            return
        else:
            logger.debug("##################### valid")
            task_item.status = 1
            task_type = task_item.type
            logger.debug("task_type=%d" % task_type)
            logger.debug(self.task_handle_funcs[task_type])
            logger.debug("33333333333333333333333333333333333333")
            
            if self.task_handle_funcs[task_type] is None:
                logger.error("invalid task type: %d" % id)
                self.invalid_task_done(task_item, constants.ERROR_MSG_TYPE_INVALID)
                return
            
            try:
                logger.debug("task_type:%d" % task_type)
                result = self.task_handle_funcs[task_type](task_item)
                self.task_done(task_item, result)
                return
            except Exception, e:
                logger.exception(e)
                self.invalid_task_done(task_item, constants.ERROR_MSG_HANDLE)
                return
        pass

    def task_done(self, task_item, result):
        if result['status_code'] == -1:
            task_item.status = -1
            task_item.msg = result['msg']
        else:
            task_item.status = 2
            if result.has_key('msg'):
                task_item.msg = result['msg']
            else:
                task_item.msg = "OK"

        percent = 100.00
        task_item.percent = ("%.2f" % percent)
        task_item.consuming = int(time.time() - self.begin_handle_time)
        logger.debug("!!!!!!!!!!!   %d" % task_item.consuming)

        self.task_done_update_dict(task_item)
        pass
            
    def task_done_print(request, result):
        #callback: not use
        pass

    def invalid_task_done(self, task_item, error_msg):
        logger.debug("")
        task_item.status = -1
        task_item.msg = error_msg
        percent = 100.00
        task_item.percent = ("%.2f" % percent)
        task_item.consuming = int(time.time() - self.begin_handle_time)

        self.task_done_update_dict(task_item)
        pass

    def task_done_update_dict(self, task_item):
        logger.debug("")
        self.unfinished_task_lock.acquire()
        del self.unfinished_task_dict[task_item.id]
        self.unfinished_task_lock.release()

        self.finished_task_lock.acquire()
        #self.finished_task_dict[task_item.id] = task_item
        self.finished_task_dict[task_item.id] = task_item
        self.finished_task_lock.release()
        logger.debug("")

    def task_status_report(self):
        sn = 'CAS1000000000'

        ret_dict = {}
        ret_dict['req'] = "host.task_status"
        ret_dict['sn'] = sn

        data_list = []
        self.unfinished_task_lock.acquire()
        logger.debug("unfinished_task_dict: \n%s" % self.unfinished_task_dict)
        for ele_key in self.unfinished_task_dict:
            logger.debug("")
            task_status_item = {}
            task_status_item['id'] = self.unfinished_task_dict[ele_key].id
            task_status_item['status'] = self.unfinished_task_dict[ele_key].status
            task_status_item['msg'] = self.unfinished_task_dict[ele_key].msg
            task_status_item['percent'] = self.unfinished_task_dict[ele_key].percent
            task_status_item['rev_time'] = self.unfinished_task_dict[ele_key].rev_time
            task_status_item['consuming'] = self.unfinished_task_dict[ele_key].consuming
            task_status_item['type'] = self.unfinished_task_dict[ele_key].type
            data_list.append(task_status_item)
        self.unfinished_task_lock.release()

        logger.debug("")
        self.finished_task_lock.acquire()
        logger.debug("22222222222222222222222222222222222")
        logger.debug("finished_task_dict: \n%s" % self.finished_task_dict)
        for ele_key in self.finished_task_dict:
            task_status_item = {}
            task_status_item['id'] = self.finished_task_dict[ele_key].id
            task_status_item['status'] = self.finished_task_dict[ele_key].status
            task_status_item['msg'] = self.finished_task_dict[ele_key].msg
            task_status_item['percent'] = self.finished_task_dict[ele_key].percent
            task_status_item['rev_time'] = self.finished_task_dict[ele_key].rev_time
            task_status_item['consuming'] = self.finished_task_dict[ele_key].consuming
            task_status_item['type'] = self.finished_task_dict[ele_key].type
            data_list.append(task_status_item)
        logger.debug("finished_task_dict: \n%s" % self.finished_task_dict)
        self.finished_task_dict.clear()
        self.finished_task_lock.release()
        logger.debug("finished_task_dict: \n%s" % self.finished_task_dict)

        task_dict = {}
        task_dict['task'] = data_list
        ret_dict['body'] = [ task_dict ]

        logger.debug("ret_dict: \n%s" % ret_dict)
        r = requests.post(constants.url_status, data=json.dumps(ret_dict))
                 
        
    def wait_for_startup_complete(self, task_item):
        """
        wait for vm setting up os
        """
        vm_name = task_item.data['vm_name']
        install_method = task_item.data['install_method']
        avm = vm(vm_name)
        if install_method == 0:
            #iso
            new_xml = avm.change_boot_type('cdrom')
            avm.edit_conf(new_xml)

        #start
        result = avm.start()
        if result['status_code'] == -1:
            return result

        new_xml = avm.change_boot_type('hd')
        avm.edit_conf(new_xml)

        check_cmd = 'virsh qemu-agent-command %s \'{"execute":"guest-ping"}\' ' % vm_name
        ok_result = '{"return":{}}\n'
        timeout = 1800
        while task_item.consuming < timeout :
            #waiting
            task_item.consuming = int(time.time() - self.begin_handle_time)
            cmd_result = commands.getoutput(check_cmd)
            if cmd_result == ok_result:
                break
            time.sleep(10)

        if task_item.consuming >= timeout:
            avm.destroy()
            avm.undefine()
            status_code = -1
            msg = "timeout"
        else:
            status_code = 0
            msg = "OK"

        ret = {}
        ret["status_code"] = status_code
        ret["msg"] = str(msg)

        return ret 

    def task_define(self, task_item):
        vm_name = task_item.data['vm_name']
        memory = task_item.data['memory']
        cpu_num = task_item.data['cpu_num']
        os_size = task_item.data['disk_os']
        data_size = task_item.data['disk_data']
        install_method = task_item.data['install_method']
        vm_file = os.path.basename(task_item.data['vm_file'])

        
        has_delete = 0
        avm = vm(vm_name)
        if avm.xml != "":
            #vm is already exist
            avm.destroy()
            avm.undefine()
            has_delete = 1

        root = construct_vm_xml(vm_name, memory, cpu_num)

        os_path,disk_list = vm.prepare_img(task_item)
        i = 1
        c_hd_xml = hd_xml("file", os_path, i)
        root.find('devices').append(c_hd_xml.tree)
        for disk_path in disk_list:
            i += 1
            c_hd_xml = hd_xml("file", disk_path, i)
            root.find('devices').append(c_hd_xml.tree)

        if install_method == 0:
            #mount iso
            c_cdrom_xml = cdrom_xml('file', constants.iso_path + '/' + vm_file, i+1)
            if c_cdrom_xml is not None:
                root.find('devices').append(c_cdrom_xml.tree)

        result = vm.define(name = vm_name, xml = ET.tostring(root))
        if result['status_code'] == 0:
            result = self.wait_for_startup_complete(task_item)

        if has_delete == 1:
            result['msg'] = "Attention: have deleted an existed vm!!  " + result['msg']
        return result
        #self.task_done(task_item, result)

        pass
        
    def task_modify(self, task_item):
        vm_name = task_item.data['vm_name']
        memory = task_item.data['mem']
        cpu_num = task_item.data['cpu']
        has_error = False
        new_xml = None
        
        avm = vm(vm_name)
        new_xml = avm.change_memory(int(memory)/1024)
        if new_xml is None:
            has_error = True
            logger.error("change_memory faild")
            
        new_xml = avm.change_cur_cpu_number(cpu_num)
        if new_xml is None:
            has_error = True
            logger.error("change_cur_cpu_number failed")
        ret = avm.extend_img(task_item)
        if ret == False:
            has_error = True
            logger.error("extend_img failed")

        logger.debug("new_xml = \n%s" % new_xml)
        if has_error:
            return {"status_code": -1, "msg":"error"}
        else:
            return avm.edit_conf(new_xml)

        pass
    def task_delete(self, task_item):
        vm_name = task_item.data['vm_name']
        delete_disk = task_item.data['delete_disk']

        avm = vm(vm_name)
        if delete_disk == 1:
            avm.delete_img()
        avm.destroy()
        result = avm.undefine()

        return result

    def task_set_ip(self, task_item):
        vm_name = task_item.data['vm_name']
        bootproto = task_item.data['bootproto']
        nic_name = task_item.data['nic_name']

        content = """DEVICE=%s\nTYPE=Ethernet\nNAME=%s\nONBOOT=yes\nBOOTPROTO=%s\n""" % (nic_name, nic_name, bootproto)
        if bootproto == "static":
            ip = task_item.data['ip']
            netmask = task_item.data['netmask']
            gateway = task_item.data['gateway']
            dns = task_item.data['dns']
            content = content + "IPADDR=%s\nNETMASK=%s\nGATEWAY=%s\nDNS3=%s\n"%(ip, netmask, gateway, dns)
        elif bootproto == "dhcp":
            pass
        else:
            logger.error("invalid nic type: %s" % bootproto)
            return {"status_code": -1, "msg":"invalid nic type"}

        path = "/etc/sysconfig/network-scripts/ifcfg-%s"%nic_name
        avm = vm(vm_name)
        ret_count = avm.write_vm_file(path, content)
        if ret_count <=0:
            return {"status_code": -1, "msg":"error"}
        else:
            ret = avm.shutdown()
            time.sleep(10)
            i = 0
            while i < 5:
                i += 1
                run_status = avm.get_status()
                if run_status['vm_status'] == constants.vm_status_shutoff:
                    break
                time.sleep(10)
            if i == 5:
                avm.destroy()
            ret = avm.start()
            return ret

    def task_action(self, task_item):
        vm_name = task_item.data['vm_name']
        action = task_item.data['action']

        result = None
        avm = vm(vm_name)
        if action == "start":
            if task_item.data.has_key('boot_type'):
                #change boot type
                boot_type = ''
                if task_item['boot_type'] == 0:
                    boot_type = 'cdrom'
                elif task_item['boot_type'] == 1:
                    boot_type = 'hd'
                else:
                    logger.error("invalid boot_type : %d" % task_item['boot_type']) 
                    boot_type = 'hd'
                new_xml = avm.change_boot_type(boot_type)
                result = avm.edit_conf(new_xml)
                if result['status_code'] == -1:
                    return result
            result = avm.start()
            return result

        elif action == "stop":
            result = avm.destroy()
            return result

        elif action == "reboot":
            result = avm.destroy()
            if result['status_code'] == -1:
                return result
            result = avm.start()
            return result
        else:
            return {"status_code": -1, "msg":"invalid action: %s" % action}

        pass
    def task_create_snapshot(self, task_item):
        vm_name = task_item.data['vm_name']
        snapshot_name = task_item.data['snapshot_name']

        avm = vm(vm_name)
        result = avm.create_snapshot(snapshot_name)
        return result
        
    def task_delete_snapshot(self, task_item):
        vm_name = task_item.data['vm_name']
        snapshot_name = task_item.data['snapshot_name']

        avm = vm(vm_name)
        result = avm.delete_snapshot(snapshot_name)
        return result

    def task_restore_snapshot(self, task_item):
        vm_name = task_item.data['vm_name']
        snapshot_name = task_item.data['snapshot_name']

        avm = vm(vm_name)
        result = avm.restore_snapshot(snapshot_name)
        return result

    def task_clone(self, task_item):
        pass

    def task_download(self, task_item):
        return self.task_download_report(task_item)

    def task_download_report(self, task_item):
        uri = task_item.data['uri']
        #size = task_item.data['size']
        #file_format = task_item.data['format']
        md5 = task_item.data['md5']
        save_path = task_item.data['save_path']

        def report(count, blockSize, totalSize):
            #update percent
            task_item.percent = ("%.2f" % (count*blockSize*100/totalSize))
            task_item.consuming = int(time.time() - self.begin_handle_time)
            pass
        filename = commands.getoutput('basename %s' % uri)
        file_abs_path = save_path + '/' + filename
        urllib.urlretrieve(uri, file_abs_path, reporthook=report)

        this_md5 = commands.getoutput("md5sum %s | awk '{print $1}' " % file_abs_path)
        if this_md5 == md5:
            return {"status_code": 0, "msg":"OK"}
        else:
            #os.system("rm -f %s" % file_abs_path)
            return {"status_code": -1, "msg":"md5 doesn't match"}
 
tm = task_manager()
tm.start()
