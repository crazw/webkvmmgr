import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 

a = vm()
ret = a.start("qemu:///system", "vm_name1")
ret = a.start("qemu:///system", "vm_name1")
ret = a.start("qemu:///system", "vm_name2")
print ret
