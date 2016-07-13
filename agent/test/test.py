import sys
import libvirt


conn = libvirt.open('qemu:///system')
if conn == None:
	print("Failed to open connection to qemu:///system', file=sys.stderr")
	exit(1)

host = conn.getHostname()
nodeinfo = conn.getInfo()
print('Hostname:'+host)
print('nodeinfo:'+nodeinfo)

conn.close()
exit(0)
