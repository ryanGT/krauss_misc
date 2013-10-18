"""
Main Classes
++++++++++++++++

This module provides two main classes and many helper functions.  The main classes are

1. :py:class:`xml_writer` is a base class for objects that will save themselves to XML files.
2. :py:class:`xml_parser` is a base class for loading and parsing XML files.

Autodoc Content
+++++++++++++++++++
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

import re, pdb


class xml_writer(object):
    """This is intended to be a base class for saving an instance of
    the object to an xml file.  Each derived class must define a
    string :py:attr:`self.xml_tag_name` and a list
    :py:attr:`self.xml_attrs` before the create_xml method is called.
    """
    def create_xml(self, root):
        """If a derived class does not override
        :py:meth:`xml_writer.create_xml`, for each element in
        :py:attr:`self.xml_attrs` a SubElement will be created with
        the name of the attr and the text for the SubElement element
        will be str(getattr(self, attr)).

        The tag name for the XML SubElement will be
        :py:attr:`self.xml_tag_name`."""
        my_elem = ET.SubElement(root, self.xml_tag_name)
        for attr in self.xml_attrs:
            if hasattr(self, attr):
                cur_xml = ET.SubElement(my_elem, attr)
                attr_str = str(getattr(self, attr))
                cur_xml.text = attr_str.encode()

        return my_elem
    

class xml_parser(object):
    """This is a base for XML parsers.  If the user does not pass in a
    filename at initialization, then they must call
    :py:meth:`xml_parser.set_root` before parsing.  This should allow
    using the same parser for a too-level object or as part of a
    larger object.  I use this approach with data_vis_gui; a figure
    parser can parse a figure XML file or be used for the figure
    portion of a larger full GUI state XML file. """
    def __init__(self, filename=None):
        self.filename = filename
        if self.filename is not None:
            self.tree = ET.parse(filename)
            self.root = self.tree.getroot()


    def set_root(self, root):
        self.root = root




def try_string_to_number(string_in):
    """This function attempts to convert a string to either an integer
    or a float.  If both conversions fail, the string is simply
    returned unmodified."""
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
    """I had some initial problems with strings saving as u'theta' and
    this is my attempt to fix that.  When reading the xml, I ended up with "u'theta'".
    I also tried to solve this problem by making sure I encoded the
    strings before saving them.  This problem was coming from the unicode version of wxPython
    and using the GetValue method of text controls."""
    q1 = p_quote1.search(string_in)
    if q1:
        return q1.group(1)
    q2 = p_quote2.search(string_in)
    if q2:
        return q2.group()
    return string_in


def clean_extra_quotes(string_in):
    """Strip extra quotes from the beginning and ending of strings."""
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
    """Replace 'None' with the actual None"""
    if string_in == 'None':
        return None
    else:
        return string_in


def clean_extra_backslashes(string_in):
    """XML saving and loading of string with latex code can lead to
    things like $\\\\theta$.  I want to search and replace the \\\\
    for \\ if the string starts and ends with $"""
    string_out = string_in.strip()
    if string_out[0] == '$' and string_out[-1] == '$':
        #we have a valid candidate
        string_out = string_out.replace('\\\\','\\')
    return string_out


def full_clean(string_in):
    """Call of my string cleaning functions in order"""
    #print('string_in = %s' % string_in)
    if string_in is None:
        return string_in
    elif type(string_in) == unicode:
        string_in = string_in.encode()
    elif type(string_in) not in [str, unicode]:
        return string_in
    string_out = string_in.strip()
    if not string_out:
        return string_out
    if string_out[0] == '[' and string_out[-1] == ']':
        return list_string_to_list(string_out)
    elif string_out[0] == '{' and string_out[-1] == '}':
        return dict_string_to_dict(string_out)
    string_out = clean_unicode(string_out)
    string_out = clean_extra_quotes(string_out)
    string_out = clean_extra_backslashes(string_out)
    string_out = clean_none_string(string_out)
    #print('string_out = %s' % string_out)
    return string_out


def prettify(elem):
    """Return a pretty-printed XML string for the Element.

    This function does successive indenting of the XML tree
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



def find_child(element, name):
    """find a child of an XML element by name; raise an exception if it isn't found"""
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
    """try searching for a child by name; return None rather than
    raising an exception if the child isn't found"""
    try:
        child = find_child(element, name)
        return child
    except ValueError:
        return None

    
def children_to_dict(element):
    """Convert the children of the element to a dictionary; the tag
    names are the key and the text of the element children are the
    values."""
    mydict = {}
    for child in element.getchildren():
        key = child.tag.strip()
        key = full_clean(key)
        if child.text:
            val = child.text.strip()
            val = full_clean(val)
        else:
            val = None
        mydict[key] = val
    return mydict


def get_child_value(element, name):
    child = find_child(element, name)
    val = child.text.strip()
    val = full_clean(val)
    return val


def get_params(element):
    """search for a child node called 'params' and convert it to a
    dictionary"""
    params_xml = find_child(element, 'params')
    params = children_to_dict(params_xml)
    return params


def get_num_params(params, sys_num_params):
    """Require all parameters to be converted to float; each parameter
    must either be converted by the float function or the val must be
    a key in sys_num_params so that sys_num_params[val] returns a
    number."""
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
    """Convert a string such as '[1,2,3]' to an actual list instance"""
    #print('string_in = ' + str(string_in))
    string0 = string_in.strip()
    if not string0:
        return string0
    if string0[0] in ['[','(']:
        string0 = string0[1:]
    if string0[-1] in [']',')']:
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
    """Convert a string such as '{'a':1, 'b':3}' to an actual
    dictionary instance"""
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
    """Write the XML of root to xmlpath after passing it through
    :py:func:`prettify`"""
    pretty_str = prettify(root)
    f = open(xmlpath, 'wb')
    f.write(pretty_str)
    f.close()


def append_dict_to_xml(root, dict_in):
    """for each key:val pair in dict_in, create a SubElement with tag
    name key and text val"""
    for key, val in dict_in.iteritems():
        val_xml = ET.SubElement(root, key)
        val_xml.text = val


def str_to_bool(str_in):
    if str_in.lower() == 'false':
        return False
    elif str_in.lower() == 'true':
        return True
    else:
        raise ValueError, 'Cannot convert this string to a bool: %s' % str_in
