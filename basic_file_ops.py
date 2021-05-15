import sys, os

def amiLinux():
    platstr=sys.platform
    platstr=platstr.lower()
    if platstr.find('linu')>-1:
        return 1
    else:
        return 0

def splittolist(pathstr):
    listout = pathstr.split(os.sep)
    while not listout[-1]:
        listout.pop()
    while not listout[0]:
        listout.pop(0)
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
        listout.append(curpath)
    if os.path.isdir(pathstr):
        listout.insert(0,pathstr)
    return listout


def FindinPath(filename):
    pathlist=sys.path
    outpath=''
    for curpath in pathlist:
        temppath=os.path.join(curpath,filename)
        if os.path.exists(temppath):
            outpath=temppath
            break
    return outpath


def FindWalkingUp(filename, pathstr=None, includesys=False):
    if pathstr is None:
        pathstr, filename = os.path.split(filename)
        if not pathstr:
            pathstr = os.getcwd()
    mypathlist = walkuplist(pathstr)
    found = 0
    if includesys:
        fullpathlist = mypathlist+os.sys.path
    else:
        fullpathlist = mypathlist
    for path in fullpathlist:
        curfp = os.path.join(path,filename)
        if os.path.exists(curfp):
            found = 1
            fp = curfp
            break
    if found:
        return fp
    else:
        return None
    

def readfile(pathin, strip=False, rstrip=True, verbosity=0):
    goodpath = None
    if os.path.exists(pathin):
        goodpath = pathin
    else:
        mypath = FindWalkingUp(pathin)
        if mypath:
            goodpath = mypath
        else:
            junk, filename = os.path.split(pathin)
            mypath=FindinPath(filename)
            if mypath:
                goodpath = mypath
            
    if goodpath:
        if verbosity > 0:
            print('found file:'+goodpath)
        f=open(goodpath,'r')
    else:
        raise OSError("Could not find "+pathin+" in sys.path")
    listin=f.readlines()
    f.close()
    if strip:
        listout = [line.strip() for line in listin]
    elif rstrip:
        listout = [line.rstrip() for line in listin]
    else:
        listout = listin
    return listout


def add_newlines(listin):
    listout = []
    for line in listin:
        if not line:
            listout.append('\n')
        elif line[-1]!='\n':
            listout.append(line+'\n')
        else:
            listout.append(line)
    return listout


def writefile(pathin, listin, append=False):
    if append and os.path.exists(pathin):
        openstr = 'a'
    else:
        openstr = 'w'
    f = open(pathin, openstr)
    listout = add_newlines(listin)
    f.writelines(listout)
    f.close()
