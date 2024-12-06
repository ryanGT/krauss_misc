import string

def remove_non_printable(str_in):
    clean_str = [letter for letter in str_in if letter in string.printable]
    str_out = ''.join(clean_str)
    return str_out

    
def label_to_attr_name(label):
    illegal_chars = [' ',':','/','\\','#','(',')',',','-','[',']','|','.','%']
    attr = label
    for char in illegal_chars:
        attr = attr.replace(char, '_')
    attr = attr.replace('__','_')
    if len(attr) > 0:
        while attr[-1] == '_':
            attr = attr[0:-1]

    attr_clean = remove_non_printable(attr)
    return attr_clean


