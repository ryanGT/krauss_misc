import os, copy, sys, glob, time, re
import pdb
import shutil
from IPython.core.debugger import Pdb

def delete_from_glob_pat(pat):
    myfiles = glob.glob(pat)
    for curpath in myfiles:
        os.remove(curpath)


def epstopdfpath(epspath):
    pne, ext = os.path.splitext(epspath)
    pdfpath = pne + '.pdf'
    return pdfpath

def get_home():
    """Get the users home directory on either windows or linux."""
    home_dir = os.getenv('HOME') or os.getenv('USERPROFILE')
    if not amiLinux():
        home_dir = home_dir.replace('/','\\')#just making sure there
                                             #are no '/'
    return home_dir

def split_list_of_paths(pathlist):
    names = []
    folders = []
    for item in pathlist:
        curfolder, curname = os.path.split(item)
        names.append(curname)
        folders.append(curfolder)
    return folders, names

def clean_filename(pathin):
    """Remove all non-alphanumeric characters (including spaces) from
    pathin, replacing with an underscore (also replaces multiple
    underscores with just one).  Does not mess with the folder, only
    the filename."""
    folder, filename = os.path.split(pathin)
    fno, ext = os.path.splitext(filename)
    out = re.sub('\W','_', fno)
    out = re.sub('_+', '_', out)
    return os.path.join(folder, out+ext)


def splittolist(pathstr):
    listout = pathstr.split(os.sep)
    while not listout[-1]:
        listout.pop()
    while not listout[0]:
        listout.pop(0)
    ## listout=[]
##     rest=copy.copy(pathstr)
##     rest, curent=os.path.split(rest)
##     if len(curent)>0:
##         listout[:0]=[curent]
##     while (len(rest)*len(curent))>0:
##         rest, curent=os.path.split(rest)
##         if len(curent)>0:
##             listout[:0]=[curent]
##     if len(rest)>0:
##         listout[:0]=[rest]
    return listout

def walkuplist(pathstr):
    sep=os.sep
    mylist=splittolist(pathstr)
    if not amiLinux():
        while mylist[0][-1]==sep:
            mylist[0]=mylist[0][0:-1]
    listout=[]
    NN = len(mylist)
    for n in range(1,NN):
        curpath = sep.join(mylist[0:NN-n])
        curpath = curpath.replace('//','/')
        listout.append(curpath)
    if os.path.isdir(pathstr):
        listout.insert(0,pathstr)
    if '/home/' in pathstr:
        droplist = ['/home','/']
        listout = [item for item in listout if item not in droplist]#don't keep /home and / if pathstr started with /home/someuser
    return listout

def makerel(fullpath):
    """Make sure that a path is relative and not full so that it is
    compatible with FindFullPath and can be used in a cross-platform
    way."""
    #user_name = os.getlogin()#apparently, this doesn't work in windows
    myhome = get_home()
    if amiLinux():
        user_name = os.getlogin()
        fullpath = fullpath.replace('\\','/')
    else:
        fullpath = fullpath.replace('/','\\')
        user_name = os.getenv('USERNAME')

    if fullpath.find(myhome) == 0:
        outpath = fullpath.replace(myhome, '')
        if outpath[0] == os.path.sep:
            outpath = outpath[1:]
    else:
        outpath = fullpath
    mylist = splittolist(outpath)
    windows_roots = ['E:','D:','C:','E:\\','D:\\','C:\\']
    if mylist[0].upper() in windows_roots:
        mylist = mylist[1:]
    elif (mylist[0].upper()=='C:' or mylist[0].upper()=='C:\\') and mylist[1].lower()==user_name:
        mylist = mylist[2:]
    elif mylist[0]=='home' and mylist[1]==user_name:
        mylist = mylist[2:]
    elif mylist[0:2]==['/','home'] or mylist[0:2]==['\\','home']:
        #assume the if the path started with /home, then the third
        #entry is user_name
        mylist = mylist[3:]
    elif mylist[0]=='mnt':
        mylist = mylist[1:]
        if mylist[0]=='e':
            mylist = mylist[1:]
    outpath = os.path.sep.join(mylist)
    return outpath

def checklower(pathin, folder=None):
    if not folder:
        folder, filename = os.path.split(pathin)
    pat = os.path.join(folder,'*')
    mylist = glob.glob(pat)
    lowlist = [item.lower() for item in mylist]
    if pathin.lower() in lowlist:
        ind = lowlist.index(pathin.lower())
        return mylist[ind]
    else:
        return None


def FindFullPath(relpath, basepaths=['Z:\\','D:\\','C:\\ryan','C:\\','E:\\']):
    outpath=''
    #print('relpath='+str(relpath))
    if amiLinux():
        homedir = os.path.expanduser('~')
        basepaths = [homedir]
        import socket
        myname = socket.gethostname()
        if myname == 'ryan-duo-laptop':
            basepaths.extend(['/mnt/RYANFAT/'])
    if relpath[0] == '~':
        home = get_home()
        relpath = os.path.join(home,relpath[1:])
    relpath = makerel(relpath)
    folder, filename = os.path.split(relpath)
    if not folder:
        curdir = os.getcwd()
        checkpath = os.path.join(curdir, filename)
        if os.path.exists(checkpath):
            return checkpath
    curdir = os.getcwd()
    if os.path.exists(relpath):
        outpath = os.path.abspath(relpath)
        return outpath
    basepaths.insert(0, curdir)
    basepaths += sys.path
    for curb in basepaths:
        curpath=os.path.join(curb,relpath)
        if os.path.exists(curpath):
            outpath=curpath
            break
    if not outpath:
        for curb in basepaths:
            curpath=os.path.join(curb,relpath)
            folder, filename = os.path.split(curpath)
            mypath = checklower(curpath, folder)
            if mypath:
                return mypath
    #print('fullpath='+outpath)
    return outpath

def FindinPath(filename):
    pathlist=sys.path
    outpath=''
    for curpath in pathlist:
        temppath=os.path.join(curpath,filename)
        if os.path.exists(temppath):
            outpath=temppath
            break
    return outpath

def CopyFromPath(filename,desfolder):
    validpath=FindinPath(filename)
    if validpath:
        shutil.copy(validpath,desfolder)
        return True
    else:
        return False

def amiLinux():
    platstr=sys.platform
    platstr=platstr.lower()
    if platstr.find('linu')>-1:
        return 1
    else:
        return 0


def find_dirs(path, hidden=False, returnrel=True):
    pattern = os.path.join(path,'*')
    myfiles=glob.glob(pattern)
    if hidden:
        pat2 = os.path.join(path,'.*')
        files2 = glob.glob(pat2)
        myfiles.extend(files2)
    mydirs=[item for item in myfiles if os.path.isdir(item)]
    mydirs2=[item for item in mydirs if item.find('System Volume Information')==-1]
    if returnrel:
        outdirs=[]
        for item in mydirs:
            junk,curdir=os.path.split(item)
            outdirs.append(curdir)
        return outdirs
    else:
        return mydirs2


def write_unison_sync_files(searchpath,outfile):
    import rwkos
    mydirs=rwkos.find_dirs(searchpath,True)
    mylist=['path = '+item+'\n' for item in mydirs]
    f=open(outfile,'w')
    f.writelines(mylist)
    f.close()
    return mylist


def FilterOutDirs(pathin, skipdirs=[]):
    if not skipdirs:
        return True
    for item in skipdirs:
        if pathin.find(item) > -1:
            return False
    return True


def FindAllSubFolders(topdir, skipdirs=[]):
    alldirs = []
    t1 = time.time()
    for root, dirs, files in os.walk(topdir):
        ta = time.time()
        #print('ta-t1='+str(ta-t1))
        if FilterOutDirs(root, skipdirs=skipdirs):
            alldirs.append(root)
        tb = time.time()
        #print('tb-ta='+str(tb-ta))
    t2 = time.time()
    #print('t2-t1='+str(t2-t1))
    return alldirs

def glob_all_subdirs(topdir, glob_pat, skipdirs=[]):
    t1 = time.time()
    alldirs = FindAllSubFolders(topdir, skipdirs=skipdirs)
    t2 = time.time()
    allmatches = None
    for curdir in alldirs:
        curpat = os.path.join(curdir, glob_pat)
        curmatches = glob.glob(curpat)
        if allmatches is None:
            allmatches = curmatches
        else:
            allmatches.extend(curmatches)
    t3 = time.time()
    #print('t3-t1='+str(t3-t1))
    #print('t2-t1='+str(t2-t1))
    return allmatches

def DirsInThisLevel(pathin):
    contents = os.listdir(pathin)
    dirs = [item for item in contents if os.path.isdir(item)]
    return dirs


def FindAllPictureFolders(topdir, skipdirs=['.comments',\
                                            'thumbnails',\
                                            '900by600']):
    return FindAllSubFolders(topdir, skipdirs=skipdirs)


def FindInSubDirs(topdir, pat, skipdirs=[]):
    t1 = time.time()
    #alldirs = FindAllSubFolders(topdir, skipdirs=skipdirs)
    alldirs = DirsInThisLevel(topdir)
    t2 = time.time()
    myfiles = []
    for curdir in alldirs:
        fullpat = os.path.join(curdir, pat)
        curfiles = glob.glob(fullpat)
        myfiles += curfiles
    t3 = time.time()
    return myfiles


def Find_in_top_and_sub_dirs(topdir, pat, skipdirs=[]):
    toppat = os.path.join(topdir, pat)
    topfiles = glob.glob(toppat)
    subfiles = FindInSubDirs(topdir, pat, skipdirs=skipdirs)
    keeptops = [item for item in topfiles if item not in subfiles]
    return keeptops + subfiles


def FindInSubDirs2(topdir, pat, searchdirs=['thumbnails','html','900by600','']):
    t1 = time.time()
    myfiles = []
    for curdir in searchdirs:
        folderpath = os.path.join(topdir, curdir)
        fullpat = os.path.join(folderpath, pat)
        curfiles = glob.glob(fullpat)
        myfiles += curfiles
    t2 = time.time()
    print('t2-t1='+str(t2-t1))
    return myfiles


def get_new_file_number(pat, destdir, startnum=1, endnum=10000):
    """Substitute the integers from startnum to endnum into pat and
    return the first one that doesn't exist.  The file name that is
    searched for is os.path.join(destdir, pat % i)."""
    for i in range(startnum, endnum):
        temp = pat % i
        if not os.path.exists(os.path.join(destdir, temp)):
            return i


def get_unique_name(pathin, destdir, fmt='%0.4d', startnum=1, \
                    forcenum=False):
    if startnum is None:
        startnum = 1
    folder, filename = os.path.split(pathin)
    if (not os.path.exists(os.path.join(destdir, filename))) and \
           (not forcenum):
        return filename
    else:
        fno, ext = os.path.splitext(filename)
        pat = fno+'_' + fmt + ext
        ind = get_new_file_number(pat, destdir)
        return pat % ind
        #t1 = time.time()


def copy_making_dirs(source_path, dest_path):
    """Copy the file from source_path to dest_path, creating whatever
    directories are necessary along the way to dest_path."""
    source_folder, source_file = os.path.split(source_path)
    dest_folder, dest_file = os.path.split(dest_path)
    assert source_file == dest_file, 'source_path and dest_file should both be full paths that end in the same file name:\n'+'source='+source_path+'\ndest='+dest_path
    mylist = dest_folder.split('/')
    curroot = '/'
    while not mylist[0]:
        mylist.pop(0)
    for folder in mylist:
        curroot = os.path.join(curroot, folder)
        #print('curroot='+curroot)
        if not os.path.exists(curroot):
            os.mkdir(curroot)
    shutil.copy2(source_path, dest_path)

def make_dir(pathin):
    """Check to see if pathin exists first, then make it if it
    doesn't.  No error is generated if pathin already exists."""
    if not os.path.exists(pathin):
        os.mkdir(pathin)


def make_dirs(paths):
    """Pass each path in the list paths to make_dir, which makes the
    directory if it doesn't already exist."""
    for path in paths:
        make_dir(path)

def make_dirs_recrusive(dir_path):
    """Split dir_path in to a list and make each dir in the tree that
    doesn't already exist."""
    sep = os.path.sep
    mylist = dir_path.split(sep)
    if amiLinux():
        curroot = '/'
    while not mylist[0]:
        mylist.pop(0)
    for folder in mylist:
        curroot = os.path.join(curroot, folder)
        #print('curroot='+curroot)
        if not os.path.exists(curroot):
            os.mkdir(curroot)



class folder(object):
    def __init__(self, root, skipdirs=[]):
        self.root = root
        self.skipdirs = skipdirs


    def find_all_subfolders(self):
        self.dirs = FindAllSubFolders(self.root, skipdirs=self.skipdirs)
        self.reldirs = [os.path.relpath(item, start=self.root) \
                        for item in self.dirs]


class picture_folder(folder):
    def __init__(self, root, \
                 skipdirs=['900by600','thumbnails','html','.comments']):
        folder.__init__(self, root, skipdirs=skipdirs)




def walk_copy_folders(root1, root2, \
                      skipdirs=['.comments', '900by600', \
                                'html', 'thumbnails'], \
                      copyfolders=False):
    """Copy folders that are in root1 but not in root2 to root2 using
    shutil.copytree"""
    if not copyfolders:
        print('='*10)
        print('')
        print('copyfolders is False, this is just a practice')
        print('')
        print('='*10)

    for root, dirs, files in os.walk(root1):
        temppath, foldername = os.path.split(root)
        if foldername not in skipdirs:
            relpath = os.path.relpath(root, start=root1)
            #print('relpath = ' + relpath)

            destpath = os.path.join(root2, relpath)
            if not os.path.exists(destpath):
                print('missing dir: ' + str(relpath))
                if copyfolders:
                    print('copying ' + relpath)
                    shutil.copytree(root, destpath)

