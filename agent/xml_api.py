import xml.etree.ElementTree as ET
from log import logger
import os,sys

class disk_xml:
    def __init__(self):
        self.disk_type = ""
        self.disk_device = ""
        self.driver_type=""
        self.target_dev=""
        self.target_bus = ""
        self.path = ""

        self.driver_cache = "none"
        #self.tree = self.init_tree()
        self.tree = None  #public 

    def init_tree(self):
        abspath = os.path.dirname(os.path.abspath(__file__))
        tree = ET.parse(abspath + '/disk.xml')
        root = tree.getroot()
        return root

    def construct_disk_xml(self):
        self.tree = ET.Element('disk')
        self.tree.attrib['type'] = self.disk_type
        self.tree.attrib['device'] = self.disk_device
        driver_element = ET.SubElement(self.tree, 'driver')
        driver_element.attrib['name'] = 'qemu'
        driver_element.attrib['type'] = self.driver_type
        driver_element.attrib['cache'] = self.driver_cache
        
        target_element = ET.SubElement(self.tree, 'target')
        target_element.attrib['dev'] = self.target_dev
        target_element.attrib['bus'] = self.target_bus
    
    def insert_readonly(self):
        ET.SubElement(self.tree, 'readonly')
    def insert_address(self):
        address_element = ET.SubElement(self.tree, 'address')
        address_element.attrib['controller'] = '0'
        address_element.attrib['type'] = 'drive'


class hd_xml(disk_xml):
    def __init__(self, disk_type, path, num, driver_type = "qcow2"):
        disk_xml.__init__(self)

        if int(num) >= 32 or int(num) <= 0 :
            logger.error("disk number is invalid")
            self.tree = None
            return 
        if not path:
            logger.error("disk path is None, invalid")
            self.tree = None
            return 

        self.disk_type = disk_type
        self.disk_device = "disk"
        self.driver_type = driver_type
        self.target_dev = 'vd' + chr(ord('a')+ int(num) - 1) 
        self.target_bus = "virtio"

        self.construct_disk_xml()
        self.insert_source(path)

        logger.debug(ET.tostring(self.tree))

    def insert_source(self, path):
        source_element = ET.SubElement(self.tree, 'source')
        if self.disk_type == "file":
            source_element.attrib['file'] = path
            pass
        elif self.disk_type == "block":
            source_element.attrib['dev'] = path
        else:
            logger.warn("disk_type is invalid")
            return None

class cdrom_xml(disk_xml):
    def __init__(self, disk_type, path, num, driver_type = "raw"):
        disk_xml.__init__(self)

        if int(num) >= 32 or int(num) <= 0 :
            logger.error("disk number is invalid")
            self.tree = None
            return 
        if not path:
            logger.error("disk path is None, invalid")
            self.tree = None
            return 

        self.disk_type = disk_type
        self.disk_device = "cdrom"
        self.driver_type = driver_type
        self.target_dev = 'hd' + chr(ord('a')+ int(num) - 1) 
        self.target_bus = "ide"

        self.construct_disk_xml()
        self.insert_source(path)
        self.insert_readonly()
        self.insert_address()

        logger.debug(ET.tostring(self.tree))

    def insert_source(self, path):
        source_element = ET.SubElement(self.tree, 'source')
        if self.disk_type == "file":
            source_element.attrib['file'] = path
            pass
        else:
            logger.warn("disk_type is invalid")
            return None


"""
def construct_disk_xml(type, path, num):

    if not path:
        logger.warn("disk path is None, invalid")
        return None
    if int(num) >= 32 or int(num) <= 0 :
        logger.warn("disk number is invalid")
        return None

    abspath = os.path.dirname(os.path.abspath(__file__))
    tree = ET.parse(abspath + '/disk.xml')
    root = tree.getroot()
    new_xml = ET.tostring(root)

    if type == "file":
        root.attrib['type'] = 'file'
        root.find('source').attrib['file'] = path
        pass
    elif type == "block":
        root.attrib['type'] = 'block'
        root.find('source').attrib['dev'] = path
    else:
        logger.warn("disk type is invalid")
        return None
    
    #"the disk's label"
    label = 'vd' + chr(ord('a')+ int(num) - 1)
    root.find('target').attrib['dev'] = label

    logger.debug(ET.tostring(root))
    return root

def construct_cdrom_xml(path, num):
    if not path:
        logger.warn("disk path is None, invalid")
        return None
    if int(num) >= 32 or int(num) <= 0 :
        logger.warn("disk number is invalid")
        return None

    abspath = os.path.dirname(os.path.abspath(__file__))
    tree = ET.parse(abspath + '/cdrom.xml')
    root = tree.getroot()
    new_xml = ET.tostring(root)

    if type == "file":
        root.attrib['type'] = 'file'
        root.find('source').attrib['file'] = path
        pass
    elif type == "block":
        root.attrib['type'] = 'block'
        root.find('source').attrib['dev'] = path
    else:
        logger.warn("disk type is invalid")
        return None
    
    #"the disk's label"
    label = 'vd' + chr(ord('a')+ int(num) - 1)
    root.find('target').attrib['dev'] = label

    logger.debug(ET.tostring(root))
    return root

"""


def construct_vm_xml(name, mem, cpu):
    abspath = os.path.dirname(os.path.abspath(__file__))
    tree = ET.parse(abspath + '/base.xml')
    root = tree.getroot()

    root.find('name').text = name

    memKB = int(mem)/1024
    root.find('memory').text = str(memKB)
    root.find('currentMemory').text = str(memKB)

    root.find('vcpu').text = str(cpu)
    agent_path = root.find('devices/channel/source').attrib['path']
    abs_agent_name = agent_path + name + '.agent'
    root.find('devices/channel/source').attrib['path'] = abs_agent_name
    
    return root 
    
def construct_snapshot_xml(name, disk_list):
    base_xml = """
        <domainsnapshot>
          <name></name>
          <disks>
          </disks>
        </domainsnapshot>
    """
    root = ET.fromstring(base_xml)
    root.find('name').text = name
    for item in disk_list:
        disk_xml = "<disk name='%s' snapshot='internal'/>" % item
        disk_ele = ET.fromstring(disk_xml)
        root.find('disks').append(disk_ele)
    return root

def extract_harddisk_labels(vm_xml):
    disk_list = []
    root = ET.fromstring(vm_xml)
    for item in root.findall('devices/disk'):
        if item.get('device') == 'disk':
            label = item.find('target').get('dev')
            if label is not None:
                disk_list.append(label)
    return disk_list

