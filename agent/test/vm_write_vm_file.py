
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from vm import vm 


a = vm('cds')
ret = a.write_vm_file("/abc.txt", "aaa=11")
print ret
print '11111111111111'

