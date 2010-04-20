import os, rwkos, rwkmisc, re, time
import pdb as Pdb

Linux = rwkos.amiLinux()

import tkFileDialog

home = rwkos.get_home()
lecturerc_name = 'pygimp_lecturerc.pkl'
lecturerc_path = os.path.join(home, lecturerc_name)
log_path = os.path.join(home, 'pygimp_log.txt')
graph_path = '/home/ryan/siue/classes/graph_paper.png'
graph_path = rwkos.FindFullPath(graph_path)

classes_base = '/home/ryan/siue/classes'
classes_base = rwkos.FindFullPath(classes_base)

keys = ['452','mechatronics','482','484','356','mobile_robotics','450']
nums = ['452','458','482','484','356','492','450']
course_num_dict = dict(zip(keys, nums))

bases = ['452/lectures', 'mechatronics/2009/lectures', '482/2009/lectures', \
         '484/lectures', '356/Fall_2009/lectures', \
         'mobile_robotics/2009/lectures']

if not Linux:
    bases = [item.replace('/','\\') for item in bases]

sep = os.path.sep

base_dict = dict(zip(keys, bases))

def log_msg(msg, clear=False):
    if clear:
        opt = 'w'
    else:
        opt = 'a'
    f = open(log_path, opt)
    time_stamp = time.strftime('%I:%M:%S %p')
    f.write(time_stamp + ': ' + msg + '\n')
    f.close()
    
def append_last_sep(pathin):
    if pathin[-1] != sep:
        pathin += sep
    return pathin
    
def get_course_key_from_path(pathin=None):
    if pathin is None:
        pathin = os.getcwd()
    #print('curdir = %s' % curdir)
    pathin = append_last_sep(pathin)
    for key in keys:
        if pathin.find(sep + key + sep) > -1:
            return key
    ## print('could not find any of %s \n' % keys)
    ## print('in curdir %s' % curdir)

def force_seps(pathin):
    if Linux:
        pathout = pathin.replace('\\','/')
    else:
        pathout = pathin.replace('/', '\\')
    return pathout

def dialog_for_lecture_path():
    classes_dir = rwkos.FindFullPath('siue/classes')
    outpath = tkFileDialog.askdirectory(initialdir=classes_dir)
    outpath = force_seps(outpath)
    return outpath

def validate_lecture_path(pathin=None, date_str=None):
    """A valid lecture path must follow the pattern
    class_root/lectures/mm_dd_yy.

    This function will append either just the date, or
    lectures/mm_dd_yy if they are missing (using the current date if
    one isn't passed in)."""
    #Pdb.set_trace()
    #log_msg('------')
    #log_msg('in validate_lecture_path')
    if pathin is None:
        pathin = os.getcwd()
    key = get_course_key_from_path(pathin)
    if not key:
        #this can't work, so we bail
        return None
    pathin = append_last_sep(pathin)
    #log_msg('pathin = %s' % pathin)
    if pathin.find(sep + 'lectures' + sep) == -1:
        temp = os.path.join(pathin, 'lectures')
        if os.path.exists(temp):
            pathin = temp
        else:
            return None
    if get_date_from_path(pathin):
        #pathin contains lectures/mm_dd_yy and is valid
        #log_msg('path has date')
        return pathin
    else:
        #log_msg('path has no date')
        if os.path.exists(pathin):
            #log_msg('path exists, appending date')
            date_str = get_cur_date_str()
            #log_msg('date_str = %s' % date_str)
            pathin = os.path.join(pathin, date_str)
            #log_msg('pathin (out) = %s' % pathin)
            if not os.path.exists(pathin):
                os.mkdir(pathin)
            return pathin
    
def find_lecture_path():
    #log_msg('------')
    #log_msg('in find_lecture_path')
    if Linux:
        curdir = os.getcwd()
        pathout = validate_lecture_path(curdir)
        if pathout:
            return pathout
    path_chosen = dialog_for_lecture_path()
    #log_msg('path_chosen = %s' % path_chosen)
    pathout = validate_lecture_path(path_chosen)
    #log_msg('pathout = %s' % pathout)
    return pathout
    
def set_lecture_path(pathin=None):
    #log_msg('------')
    #log_msg('in set_lecture_path')
    if os.path.exists(lecturerc_path):
        mydict = rwkmisc.LoadPickle(lecturerc_path)
    else:
        mydict = {}
    if pathin is None:
        pathin = find_lecture_path()
    mydict['lecture_path'] = pathin
    #log_msg('setting lecture_path to %s' % mydict['lecture_path'])
    rwkmisc.SavePickle(mydict, lecturerc_path)
    return mydict['lecture_path']

def get_path_from_pkl():
    if os.path.exists(lecturerc_path):
        mydict = rwkmisc.LoadPickle(lecturerc_path)
        loaded_path = mydict['lecture_path']
        #log_msg('loading path from pickle: %s' % loaded_path)
        return loaded_path
    else:
        return set_lecture_path()

def get_course_key():
    lecture_path = get_path_from_pkl()
    key = get_course_key_from_path(lecture_path)
    return key

def get_course_number():
    key = get_course_key()
    if key:
        cn = course_num_dict[key]
        return cn

## def get_lecture_base():
##     """Load full lecture path (that includes the date) from the
##     settings pkl"""
##     key = get_course_key()
##     if key:
##         base = base_dict[key]
##         lecture_base = os.path.join(classes_base, base)
##         return lecture_base

## def get_course_number():
##     key = get_course_key_from_curdir()
##     if key:
##         cn = course_num_dict[key]
##         return cn

#lb = get_lecture_base()
#print('lecture_base = %s' % lb)

def get_cur_date_str():
    date_str = time.strftime('%m_%d_%y')
    return date_str

def get_date_from_path(pathin=None):
    if pathin is None:
        pathin = os.getcwd()
    if Linux:
        p = re.compile('/lectures/(\d+_\d+_\d+)')
    else:
        p = re.compile('\\\\lectures\\\\(\d+_\d+_\d+)')#re backslash plague
    q = p.search(pathin)
    if q:
        #q.group(1).split('_',2)
        return q.group(1)
    else:
        return None

def get_date_for_slide():
    lecture_path = get_path_from_pkl()
    date_str = get_date_from_path(lecture_path)
    return date_str
    
## def get_date_str():
##     date_str = get_date_for_slide()
##     if not date_str:
##         date_str = get_cur_date_str()
##     return date_str

def get_date_folder():
    date_str = get_date_for_slide()
    lecture_base = get_path_from_pkl()
    folder = os.path.join(lecture_base, date_str)
    return folder

def get_slide_num_filename(myint=None, pat=None):
    date_str = get_date_for_slide()
    folder = get_path_from_pkl()
    #log_msg('folder=%s' % folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    if pat is None:
        cn = get_course_number()
        pat = 'ME' + cn+ '_'+date_str+'_%0.4d.png'
    #log_msg('myint=%s' % myint)
    if myint is None:
        new_ind = rwkos.get_new_file_number(pat, folder)
    else:
        new_ind = myint
    #log_msg('new_ind=%s' % new_ind)
    new_name = pat % new_ind
    return new_name, new_ind


