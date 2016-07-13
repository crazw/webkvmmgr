import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 

a = vm()
ret = a.get_status("qemu:///system", "cds")
ret = a.get_status("qemu:///system", "louzhengwei")

print ret
