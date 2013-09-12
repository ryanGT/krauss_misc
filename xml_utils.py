import xml.etree.ElementTree as ET
from xml.dom import minidom

import re

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



def find_child(element, name):
    found = 0
    for child in element.getchildren():
        if child.tag == name:
            found = 1
            break

    if found:
        return child
    else:
        raise ValueError, "did not find child with tag name %s in %s" % \
              (name, element.getchildren())


def children_to_dict(element):
    mydict = {}
    for child in element.getchildren():
        key = child.tag.strip()
        val = child.text.strip()
        mydict[key] = val
    return mydict


def get_params(element):
    params_xml = find_child(element, 'params')
    params = children_to_dict(params_xml)
    return params


def get_num_params(params, sys_num_params):
    params_out = {}

    for key, val in params.iteritems():
        valout = None
        try:
            valout = float(val)
        except ValueError:
            valout = sys_num_params[val]

        assert valout is not None, 'problem with %s:%s' % (key,val)
        params_out[key] = valout

    return params_out


def try_string_to_float(string_in):
    try:
        myout = float(string_in)
    except:
        myout = string_in
    return myout

pat1 = r"u'(.*)'"
pat2 = r'u"(.*)"'
p_quote1 = re.compile(pat1)
p_quote2 = re.compile(pat2)

def clean_unicode(string_in):
    q1 = p_quote1.search(string_in)
    if q1:
        return q1.group(1)
    q2 = p_quote2.search(string_in)
    if q2:
        return q2.group()
    return string_in


def list_string_to_list(string_in):
    string0 = string_in.strip()
    if string0[0] == '[':
        string0 = string0[1:]
    if string0[-1] == ']':
        string0 = string0[0:-1]
    
    mylist = string0.split(',')
    #solve problems with unicode strings that match the pattern with u'name'
    mylist00 = [clean_unicode(item) for item in mylist]
    mylist0 = [label.encode() for label in mylist00]
    mylist2 = [label.strip() for label in mylist0]
    mylist3 = [try_string_to_float(item) for item in mylist2]
    return mylist3


def dict_string_to_dict(string_in):
    string0 = string_in.strip()
    if string0[0] == '{':
        string0 = string0[1:]
    if string0[-1] == '}':
        string0 = string0[0:-1]
    dict_list = string_in.split(',')
    dict_out = {}

    for cur_str in dict_list:
        key, val = cur_str.split(':',1)
        key = key.strip()
        key = clean_unicode(key)
        val = val.strip()
        val = clean_unicode(val)
        val = val.replace('\\\\','\\')
        dict_out[key] = try_string_to_float(val)

    return dict_out


def write_pretty_xml(root, xmlpath):
    pretty_str = prettify(root)
    f = open(xmlpath, 'wb')
    f.write(pretty_str)
    f.close()


def append_dict_to_xml(root, dict_in):
    for key, val in dict_in.iteritems():
        val_xml = ET.SubElement(root, key)
        val_xml.text = val


class xml_writer(object):
    """This is intended to be a base class for saving an instance of
    the object to an xml file.  Each derived class must define a
    string self.xml_tag_name and a list self.xml_attrs before the
    create_xml method is called.
    """
    def create_xml(self, root):
        my_elem = ET.SubElement(root, self.xml_tag_name)
        for attr in self.xml_attrs:
            cur_xml = ET.SubElement(my_elem, attr)
            attr_str = str(getattr(self, attr))
            cur_xml.text = attr_str.encode()


class xml_parser(object):
    def __init__(self, filename):
        self.filename = filename
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()


