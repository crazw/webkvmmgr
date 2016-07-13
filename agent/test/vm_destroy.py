import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 

a = vm()
ret = a.destroy("qemu:///system", sys.argv[1])
print ret
