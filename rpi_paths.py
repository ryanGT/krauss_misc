import os, sys

mygitpaths = ['research','krauss_misc']

def append_my_paths(base='/home/pi/git'):
    for curpath in mygitpaths:
        fullpath = os.path.join(base, curpath)
        if fullpath not in sys.path:
            sys.path.append(fullpath)
            
