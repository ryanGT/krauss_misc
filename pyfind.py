import glob, os

from IPython.core.debugger import Pdb

def findall(topdir, pat, walk=True, includetop=1):
    if includetop:
        curpat = os.path.join(topdir, pat)
        myfiles = glob.glob(curpat)
    else:
        myfiles = []
    if walk:
        for root, dirs, files in os.walk(topdir):
            for curdir in dirs:
                curpath = os.path.join(root,curdir)
                curpat = os.path.join(curpath, pat)
                curfiles = glob.glob(curpat)
                myfiles.extend(curfiles)
    return myfiles

