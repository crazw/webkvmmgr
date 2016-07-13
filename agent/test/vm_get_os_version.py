import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 
import libvirt

a = vm('cds')
conn = libvirt.open("qemu:///system")

ret = a.get_os_version()


print ret
