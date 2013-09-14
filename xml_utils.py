import xml.etree.ElementTree as ET
from xml.dom import minidom

import re, pdb

def try_string_to_number(string_in):
    try:
        myout = int(string_in)
    except:
        try:
            myout = float(string_in)
        except:
            myout = string_in
    return myout

pat1 = r"^u'(.+?)'"
pat2 = r'^u"(.+?)"'
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


def clean_extra_quotes(string_in):
    string0 = string_in.strip()
    if not string0:
        return string0
    if string0[0] == '"':
        string0 = string0[1:]
    if string0[0] == "'":
        string0 = string0[1:]
    if string0[-1] == '"':
        string0 = string0[0:-1]
    if string0[-1] == "'":
        string0 = string0[0:-1]
    return string0


def clean_none_string(string_in):
    if string_in == 'None':
        return None
    else:
        return string_in


def full_clean(string_in):
    #print('string_in = %s' % string_in)
    string_out = string_in.strip()
    string_out = clean_unicode(string_out)
    string_out = clean_extra_quotes(string_out)
    string_out = clean_none_string(string_out)
    #print('string_out = %s' % string_out)
    return string_out


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


def find_child_if_it_exists(element, name):
    try:
        child = find_child(element, name)
        return child
    except ValueError:
        return None

    
def children_to_dict(element):
    mydict = {}
    for child in element.getchildren():
        key = child.tag.strip()
        key = full_clean(key)
        val = child.text.strip()
        val = full_clean(val)
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




def list_string_to_list(string_in):
    #print('string_in = ' + str(string_in))
    string0 = string_in.strip()
    if string0[0] == '[':
        string0 = string0[1:]
    if string0[-1] == ']':
        string0 = string0[0:-1]
    
    mylist = string0.split(',')
    #solve problems with unicode strings that match the pattern with u'name'
    #mylist00 = [clean_unicode(item) for item in mylist]
    #mylist00A = [clean_extra_quotes(item) for item in mylist00]
    mylist00 = [full_clean(item) for item in mylist]
    mylist0 = [label.encode() for label in mylist00]
    mylist2 = [label.strip() for label in mylist0]
    mylist3 = [try_string_to_number(item) for item in mylist2]
    ## print('items out:')
    ## for item in mylist3:
    ##     print(item)

    return mylist3


def dict_string_to_dict(string_in):
    string0 = string_in.strip()
    if string0[0] == '{':
        string0 = string0[1:]
    if string0[-1] == '}':
        string0 = string0[0:-1]
    dict_list = string0.split(',')
    dict_out = {}

    for cur_str in dict_list:
        key, val = cur_str.split(':',1)
        key = key.strip()
        key = full_clean(key)
        if key == 'selected_inds':
            pdb.set_trace()
        ## key = clean_unicode(key)
        ## key = clean_extra_quotes(key)
        val = val.strip()
        ## val = clean_unicode(val)
        ## val = clean_extra_quotes(val)
        val = full_clean(val)
        val = val.replace('\\\\','\\')
        dict_out[key] = try_string_to_number(val)

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
    def __init__(self, filename=None):
        self.filename = filename
        if self.filename is not None:
            self.tree = ET.parse(filename)
            self.root = self.tree.getroot()


    def set_root(self, root):
        self.root = root


