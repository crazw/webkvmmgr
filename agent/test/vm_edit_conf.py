import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vm import vm 
import libvirt

a = vm("cds")
conn = libvirt.open("qemu:///system")
a.change_cur_cpu_number(conn, 4)
a.change_cur_cpu_number(conn, 1)
a.change_cur_cpu_number(conn, 20)

a.change_memory(1024000)
a.change_memory(4024000)
print ret
