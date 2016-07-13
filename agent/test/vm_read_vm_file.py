
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from vm import vm 


a = vm('cds')
ret = a.read_vm_file("/proc/diskstats")
ret = a.read_vm_file("/proc/net/dev")
print ret
ret = a._get_network_interfaces()
print ret
print '11111111111111'
