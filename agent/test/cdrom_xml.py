import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from xml_api import cdrom_xml 

cdrom_xml("block", "_path", 1)
cdrom_xml("file", "_path", 2)
cdrom_xml("block", "_path", 100)
#disk_xml('block', 'aaa/a', 1)
#disk_xml('file', 'aaa/a', 2)
