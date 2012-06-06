import os, rwkos, rwkmisc, re, time
import pdb as Pdb

from gimpfu import *

Linux = rwkos.amiLinux()

import tkFileDialog

autosave_dir = '/home/ryan/gimpautosave/'

home = rwkos.get_home()
lecturerc_name = 'pygimp_lecturerc.pkl'
lecturerc_path = os.path.join(home, lecturerc_name)
log_path = os.path.join(home, 'pygimp_log.txt')
graph_path = '/home/ryan/siue/classes/graph_paper_2000_by_1300.png'
graph_path = rwkos.FindFullPath(graph_path)

classes_base = '/home/ryan/siue/classes'
classes_base = rwkos.FindFullPath(classes_base)

keys = ['452','mechatronics','482','484','356','mobile_robotics','450']
nums = ['452','458','482','484','356','492','450']
course_num_dict = dict(zip(keys, nums))

bases = ['452/lectures', 'mechatronics/2009/lectures', '482/2009/lectures', \
         '484/lectures', '356/Fall_2009/lectures', \
         'mobile_robotics/2010/lectures']

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


def open_pickle():
    mydict = rwkmisc.LoadPickle(lecturerc_path)
    return mydict


def save_pickle(mydict):
    rwkmisc.SavePickle(mydict, lecturerc_path)

    
def folder_from_pickle():
    mydict = open_pickle()
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
        pat = 'ME' + cn + '_'+date_str+'_%0.4d.png'
    #log_msg('myint=%s' % myint)
    if myint is None:
        new_ind = rwkos.get_new_file_number(pat, folder)
    else:
        new_ind = myint
    #log_msg('new_ind=%s' % new_ind)
    new_name = pat % new_ind
    return new_name, new_ind


def get_slide_num_filename_2010(myint=None):
    mydict = open_pickle()
    pat = mydict['pat']
    folder = mydict['lecture_path']
    if myint is None:
        new_ind = rwkos.get_new_file_number(pat, folder)
    else:
        new_ind = myint
    #log_msg('new_ind=%s' % new_ind)
    new_name = pat % new_ind
    return new_name, new_ind


def _valid_filename(curname, full_pat):
    if curname.find(full_pat) == 0:
        return True
    elif curname.find(autosave_dir) == 0:
        #this is an autosaved image we are trying to recover
        autosave_folder, autosaved_name = os.path.split(curname)
        lecture_folder, short_pat = os.path.split(full_pat)
        if autosaved_name.find(short_pat) == 0:
            return True
        else:
            return False
        

def _is_recovery_file(curname):
    if curname.find(autosave_dir) == 0:
        return True
    else:
        return False
    
    
def save_all_slides():
    img_list = gimp.image_list()
    N = len(img_list)
    
    print('img_list = ' + str(img_list))
    mydict = open_pickle()
    full_pat = os.path.join(mydict['lecture_path'], mydict['search_pat'])
    success = True
    for img in img_list:
        curname = img.filename
        if _is_recovery_file(curname):
            print('this is a recovery file')
            #force the image to be dirty
            img.layers[0].visible = False
            img.layers[0].visible = True

        if curname and _valid_filename(curname, full_pat):
            if pdb.gimp_image_is_dirty(img):
                out = my_save_2010(img)
                if not out:
                    #if any one save fails, success is False
                    success = False
            else:
                print('not saving clean image: ' + curname)
    return success



def close_all(N=10):
    if gimp.image_list():
        for i in range(N):
            disp = gimp._id2display(i)
            if disp is not None:
                #Pdb.set_trace()
                try:
                    pdb.gimp_display_delete(disp)
                except:
                    print('problem deleting disp # ' + str(i))


def _save_and_close(save=True, close=True):
    if save:
        success = save_all_slides()
    if close and success:
        close_all()
    return success


def my_save_2010(img, drawable=None):
    path1 = img.filename

    if check_for_floating(img):
        #exit this method
        return False

    mydict = open_pickle()
    folder = mydict['lecture_path']
    search_pat = mydict['search_pat']
    search_folder = os.path.join(folder, search_pat)
    #Test 1
    if path1.find(search_folder) != 0:
        if path1.find(autosave_dir) == 0:
            junk, filename = os.path.split(path1)
            path1 = os.path.join(folder, filename)
            print('setting path1 to ' + path1)
        else:
            print('problem with filename: ' + path1)
            return False

    #Test 2
    myint = get_notes_layer_slide_num(img)
    name2 = mydict['pat'] % myint
    path2 = os.path.join(folder, name2)

    int3 = mydict['current_slide']
    #if (int3 == myint) and (path1 == path2):
    print('path1 = ' + path1)
    print('path2 = ' + path2)

    if path1 == path2:
        #We have a pretty sure match
        _really_save(img, path1)    
    else:
        png_path = save_as(initialdir=folder, \
                           initialfile=new_name)
        _really_save(img, png_path)
    return True


def check_for_floating(img):
    for layer in img.layers:
        if layer.name == 'Pasted Layer':
            slide_num = slide_num_from_path(img.filename)
            msg = 'Please anchor floating selection for slide %i' % slide_num
            W = tk_msg_dialog.myWindow(msg)
            return True


def save_as(initialdir=None, initialfile=None):
    filename = tkFileDialog.asksaveasfilename(initialdir=initialdir, \
                                              initialfile=initialfile, \
                                              filetypes=filetypes)
    return filename


def save_as_jpg(initialdir=None, initialfile=None):
    filename = tkFileDialog.asksaveasfilename(initialdir=initialdir, \
                                              initialfile=initialfile, \
                                              filetypes=jpgtypes)
    return filename


def find_graph_ind(img, name='graph_paper_2000_by_1300.png'):
    N = len(img.layers)
    for n in range(N):
        if img.layers[n].name.find('graph_paper') == 0:
            #img.layers[n].name == name:
            return n


def find_notes_layer(img, name='Notes Layer'):
    N = len(img.layers)
    for n in range(N):
        if img.layers[n].name.find(name) == 0:
            return n


def get_notes_layer_slide_num(img, name='Notes Layer'):
    ind = find_notes_layer(img, name)
    layer_name = img.layers[ind].name
    N = len(name)
    rest = layer_name[N:]
    #log_msg('rest:'+rest)
    rest = rest.strip()
    if rest:
        myint = int(rest)
        log_msg('myint:%i'%myint)
        return myint
    else:
        return None


def rst_is_blank(pathin, verbosity=1):
    f = open(pathin, 'rb')
    mylines = f.readlines()
    f.close()
    cleanlines = [line.strip() for line in mylines]
    nonempty = [line for line in cleanlines if line]
    N = len(nonempty)
    mybool = bool(N < 3)
    if mybool and (verbosity > 0):
        print('rst is assumed to be blank (if has less than two lines): \n' + \
              pathin)
    return mybool


def _really_save(img, savepath):
    ind = find_graph_ind(img)

    if ind:
        img.layers[ind].visible = False

    pne, ext = os.path.splitext(savepath)
    xcf_path = pne + '.xcf'
    png_path = pne + '.png'
    pdb.gimp_selection_all(img)
    pdb.gimp_edit_copy_visible(img)
    img2 = pdb.gimp_edit_paste_as_new()
    drawable = img.layers[0]
    pdb.gimp_xcf_save(1, img, drawable, xcf_path, xcf_path)
    #img.filename = xcf_path
    flat_layer = pdb.gimp_image_flatten(img2)
    #gimp.Display(img2)
    pdb.gimp_file_save(img2, flat_layer, png_path, png_path)
    pdb.gimp_image_delete(img2)
    if ind:
        img.layers[ind].visible = True
    pdb.gimp_image_clean_all(img)
    gimp.displays_flush()


def save_flattened_copy(img, savepath):
    pdb.gimp_selection_all(img)
    pdb.gimp_edit_copy_visible(img)
    img2 = pdb.gimp_edit_paste_as_new()
    flat_layer = pdb.gimp_image_flatten(img2)
    #gimp.Display(img2)
    pdb.gimp_file_save(img2, flat_layer, savepath, savepath)
    pdb.gimp_image_delete(img2)
    #pdb.gimp_image_clean_all(img)
    #gimp.displays_flush()


def folder_and_pngpath_from_rstpath(rstpath):
    folder, rstname = os.path.split(rstpath)
    filename, ext = os.path.splitext(rstname)
    pngname = filename + '1.png'
    pngpath = os.path.join(folder, pngname)
    return folder, pngpath


def rst_to_png_one_path(rstpath):
    if os.path.exists(rstpath):
        if not rst_is_blank(rstpath):
            folder, pngpath = folder_and_pngpath_from_rstpath(rstpath) 
            run_this_one = True
            if os.path.exists(pngpath):
                pngmtime = os.path.getmtime(pngpath)
                rstmtime = os.path.getmtime(rstpath)
                if rstmtime < pngmtime:
                    run_this_one = False
            if run_this_one:
                cmd = '/home/ryan/scripts/rst_outline_gen.py ' + rstpath
                os.system(cmd)
    

def rst_to_png_all_three():
    filenames = ['outline','announcements','reminders']
    folder = folder_from_pickle()
    exclude_dir = os.path.join(folder, 'exclude')
    for filename in filenames:
        rstname = filename + '.rst'    
        rstpath = os.path.join(exclude_dir, rstname)
        rst_to_png_one_path(rstpath)


def slide_num_from_path(filepath):
    folder, name = os.path.split(filepath)
    fno, ext = os.path.splitext(name)
    int_str = fno[-4:]
    cur_slide = int(int_str)
    return cur_slide
