import os,sys
import libvirt

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from host import vmmhost 
from vm import vm

cvm = vm()
conn = libvirt.open("qemu:///system")
chost = vmmhost('123123', conn)
ret = chost.download_res("http://download.microsoft.com/download/B/8/9/B898E46E-CBAE-4045-A8E2-2D33DD36F3C4/vs2015.pro_chs.iso", "123","/home/louzhengwei/test/sdb2/iso/" )
print ret

#print ret
