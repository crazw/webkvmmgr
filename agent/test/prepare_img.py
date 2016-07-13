task_dict ={    "create_time": "2010-01-01 00:00:00",     "id":1,    "age": 3600,    "type": 1,    "vm_name": "xingyu",    "formula": "",    "topology" : { "cpu" : 1, "disk" : 1},    "cpu_num":2,    "memory":512000000,    "disk_os":30,    "disk_data":100,    "install_method": 0,    "vm_file": "/home/iso/centos6.7-for-xingyu.iso",    "father_id": 1}

import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 
import task

a = vm("cds")
ctask = task.task(task_dict)
a.prepare_img(ctask)

