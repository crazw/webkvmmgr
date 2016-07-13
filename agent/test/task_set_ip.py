task_dict ={    "create_time": "2018-01-01 00:00:00",     "id":1,    "age": 3600,   
    "type": 8,    "vm_name": "cds",    "formula": "",    "topology" : { "cpu" : 1, "disk" : 1},  
    "cpu_num":2, 
    "memory":512000000,  
    "disk_os":30000000,  
    "disk_data":1000000000,
    "sysdisk_extend":5000000,
    "datadisk_extend":5000000,
    "mem":1000,
    "cpu":3,
    "install_method": 0,
    "vm_file": "/home/iso/centos6.7-for-xingyu.iso",  
    "father_id": 1,
    "uri":"http://download.microsoft.com/download/B/8/9/B898E46E-CBAE-4045-A8E2-2D33DD36F3C4/vs2015.pro_chs.iso",
    "save_path":"/home/",
    "md5": "111",
    "bootproto":"static",
    "ip":"192.168.1.46",
    "dns":"8.8.8.8",
    "gateway":"192.168.1.1",
    "netmask":"255.255.255.0",
    "nic_name":"bond0",



}

task_dict2 ={    "create_time": "2010-01-01 00:00:00",     "id":1,    "age": 3600,   
    "type": 1,    "vm_name": "xingyu",    "formula": "",    "topology" : { "cpu" : 1, "disk" : 1},  
    "cpu_num":2, 
    "memory":512000000,  
    "disk_os":30,  
    "disk_data":100,
    "install_method": 1,
    "vm_file": "/home/iso/centos6.7-for-xingyu.iso",  
    "father_id": 1,
    "uri":"http://download.microsoft.com/download/B/8/9/B898E46E-CBAE-4045-A8E2-2D33DD36F3C4/vs2015.pro_chs.iso",
    "save_path":"/home/",
    "md5": "111",


}
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 
from host import vmmhost 
import task

a = vm("cds")
#a.write_vm_file("/etc/sysconfig/network-scripts/ifcfg-bond0", "aaaaa")
tm = task.task_manager()
ctask = task.task(task_dict)

tm.task_set_ip(ctask)

