import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from xml_api import hd_xml 

hd_xml('block', 'aaa/a', 1)
hd_xml('file', 'aaa/aa', 2)

