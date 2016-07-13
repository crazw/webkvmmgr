import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from xml_api import construct_snapshot_xml 
import xml.etree.ElementTree as ET

root = construct_snapshot_xml("name1", ["22", "32"])
print ET.tostring(root)

