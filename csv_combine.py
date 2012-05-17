import glob, os, sys

import txt_mixin

from IPython.core.debugger import Pdb

def find_pathout(glob_pat):
    first, last = glob_pat.split('$',1)
    pathout = first+'.csv'
    return pathout


def find_all_files(glob_pat):
    allfiles = glob.glob(glob_pat)
    return allfiles


def make_pat2(glob_pat):
    pat2 = glob_pat.replace('*', '%i')
    return pat2


def combined_csvs(allfiles, pathout, pat2):
    N = len(allfiles)
    if os.path.exists(pathout):
        os.remove(pathout)
    outfile = txt_mixin.txt_file_with_list(pathout)

    for i in range(1,N+1):
        curfile = pat2 % i
        outfile.append_file_to_list(curfile)


    outfile.writefile(pathout)

    return outfile


def run(glob_pat, pathout=None):
    if pathout is None:
        pathout = find_pathout(glob_pat)
    allfiles = find_all_files(glob_pat)
    pat2 = make_pat2(glob_pat)
    outfile = combined_csvs(allfiles, pathout, pat2)



