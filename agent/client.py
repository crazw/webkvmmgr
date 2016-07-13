import requests
from log import logger
import json
import datetime
from vm import vm
from host import vmmhost
import libvirt
import constants
import Queue
import time 
import os

"""
url_up = 'http://192.168.1.136:8000/api/kvm'
#headers = {'content-type': 'application/json'}
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.post(url_up, data=json.dumps(payload))
"""

def get_now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
def build_vm_conf(sn, uri = "qemu:///system"):

    conn = None
    try:
        conn = libvirt.open(uri)
    except Exception, e:
        logger.exception(e)

    ret_dict = {}
    ret_dict['req'] = "vm.conf"
    ret_dict['sn'] = sn

    doms_info = []
    chost = vmmhost(sn, conn)
    now_time = get_now_str()
    for name in chost.get_vmlist():
        dom_info = {}
        dom_info['name'] = name 
        dom_info['update_time'] = now_time
        dom_info['type'] = 0
        avm = vm(name)
        dom_info['os'] = avm.get_os_version() #todo: lsb_release -d
        dom_info['cpu_num'] = avm.get_cpu_num()
        dom_info['memory'] = avm.get_mem()
        dom_info['disk'] = avm.get_disk_info()
        dom_info['network'] = avm.get_net_info()
        snapshot_list = avm.get_snapshots()
        snapshot_list_info = []
        for item in snapshot_list:
            snap_item = {}
            snap_item['name'] = item
            snap_item['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  #todo
            snap_item['comment'] = "xxxx" 
            snapshot_list_info.append(snap_item)
        dom_info['snapshots'] = snapshot_list_info

        doms_info.append(dom_info)

    ret_dict['body'] = doms_info
    logger.debug('---------------------------------------------------')
    logger.debug(ret_dict)

    if conn:
        conn.close()

    return ret_dict

def build_vm_status(sn, uri = "qemu:///system"):

    conn = None
    try:
        conn = libvirt.open(uri)
    except Exception, e:
        logger.exception(e)

    ret_dict = {}
    ret_dict['req'] = "vm.status"
    ret_dict['sn'] = sn

    doms_info = []
    chost = vmmhost(sn, conn)
    now_time = get_now_str()
    for name in chost.get_vmlist():
        print name
        dom_info = {}
        dom_info['name'] = name 
        dom_info['update_time'] = now_time

        avm = vm(name)
        run_status = avm.get_status()
        dom_info['status'] = run_status['vm_status']

        
        if dom_info['status'] == constants.vm_status_running:

            vm_info = avm.get_info()
            dom_info['cpu_idle'] = vm_info['cpu_idle']
            dom_info['mem_usage'] = vm_info['mem_usage']
            dom_info['disk'] = [] #todo
            net_item = {}
            net_item['name'] = ""
            dom_info['net'] = avm._get_network_interfaces() 
        else:
            dom_info['cpu_idle'] = 100.00
            dom_info['mem_usage'] = 0.00
            dom_info['disk'] = [] 
            dom_info['net'] = [] 

        doms_info.append(dom_info)

    ret_dict['body'] = doms_info

    logger.debug(ret_dict)

    if conn:
        conn.close()

    return ret_dict

def build_host_hw(sn, uri = "qemu:///system"):

    conn = None
    try:
        conn = libvirt.open(uri)
    except Exception, e:
        logger.exception(e)

    ret_dict = {}
    ret_dict['req'] = "host.hw"
    ret_dict['sn'] = sn

    chost = vmmhost(sn, conn)

    ret_dict['body'] = [ chost.get_hw_info() ]

    if conn:
        conn.close()

    return ret_dict

def build_host_status(sn, uri = "qemu:///system"):

    conn = None
    try:
        conn = libvirt.open(uri)
    except Exception, e:
        logger.exception(e)

    ret_dict = {}
    ret_dict['req'] = "host.status"
    ret_dict['sn'] = sn

    chost = vmmhost(sn, conn)
    host_info = chost.get_sw_info()
    host_info['name'] = chost.get_hostname()
    host_info['status'] = 1
    host_info['update_time'] = get_now_str()
    host_info['task'] = []   #todo


    host_info['mem_usage'] = chost.get_memory_usage()['mem_usage']
    host_info['cpu_idle'] = ("%.2f" % (100- float(chost.get_cpu_usage()['cpu_usage'])))
    host_info['disk'] = chost.get_disk_usage()
    host_info['net'] = chost.get_net_usage() 
    #todo
    host_info['ip'] = str(chost.get_out_ip()) 
    host_info['disk_usage'] = 20 #%.2f

    #todo: filter files by 'iso/ISO'
    vm_files = []
    vm_file_item = {}
    
    for i in os.listdir(constants.iso_path):
        abs_path = os.path.join(constants.iso_path, i)
        if os.path.isfile(abs_path):
            vm_file_item={}
            vm_file_item['name'] = i
            vm_file_item['type'] = 0
            vm_file_item['size'] = os.path.getsize(abs_path)
            vm_file_item['path'] = constants.iso_path
            vm_files.append(vm_file_item)

    for i in os.listdir(constants.img_template_path):
        abs_path = os.path.join(constants.img_template_path, i)
        if os.path.isfile(abs_path):
            vm_file_item={}
            vm_file_item['name'] = i
            vm_file_item['type'] = 0
            vm_file_item['size'] = os.path.getsize(abs_path)
            vm_file_item['path'] = constants.img_template_path
            vm_files.append(vm_file_item)
 
    host_info['vm_files'] = vm_files

    ret_dict['body'] = [ host_info ]

    if conn:
        conn.close()

    logger.debug(ret_dict)
    return ret_dict


def start():
    sn = 'CAS1000000000'
    try:
        payload = build_host_hw(sn)
        logger.debug(json.dumps(payload))
        r = requests.post(constants.url_status, data=json.dumps(payload))
    except Exception, e:
        logger.exception(e)
    while 1:

        try:
            payload = build_host_status(sn)
            r = requests.post(constants.url_status, data=json.dumps(payload))
            print r.status_code

            payload = build_vm_conf(sn)
            r = requests.post(constants.url_status, data=json.dumps(payload))
            print r.status_code

            payload = build_vm_status(sn)
            r = requests.post(constants.url_status, data=json.dumps(payload))
            print r.status_code
        except Exception, e:
            logger.exception(e)

        time.sleep(5)



start()
exit()

"""

_task_wait_list = []
_task_doing_list = []

def dispatch():
    while 1:
        time.sleep(1)
        lock _task_wait_list
        if len(_task_wait_list) != 0:
            pop 
            get thread to do task
        unlock _task_wait_list

def get_task_status():
    pass
    

"""
def task_is_expired(task_item):
    pass
def task_handling(task_item):
    
    pass
def task_done(task_item):
    pass

#pool = threadpool.ThreadPool(10)
#start()




    

