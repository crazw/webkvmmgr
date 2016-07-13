
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from vm import vm 


a = vm()
ret = a.start_from_cdrom("qemu:///system", "vm_name1", "cdrom_name1")
print ret
