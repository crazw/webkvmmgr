import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from xml_api import hd_xml 

hd = hd_xml("block", "_path", 1)
hd = hd_xml("file", "_path", 2)
hd = hd_xml("block", "_path", 100)
#disk_xml('block', 'aaa/a', 1)
#disk_xml('file', 'aaa/a', 2)
