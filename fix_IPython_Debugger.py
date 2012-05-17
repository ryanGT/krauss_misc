import txt_mixin

def fix_one_file(pathin):
    #from IPython.core.debugger import Pdb
    myfile = txt_mixin.txt_file_with_list(pathin)
    #old_inds = myfile.list.findallre('from +IPython.Debugger', match=0)
    old_inds = myfile.list.findall('IPython.Debugger')
    new_inds = myfile.list.findall('from IPython.core.debugger')

    new_line = 'from IPython.core.debugger import Pdb'

    if old_inds and not new_inds:
        for ind in old_inds:
            myfile.list[ind] = new_line

    elif (len(old_inds) == len(new_inds)):
        #assume I commented out the old and inserted the new
        for ind in old_inds:
            if myfile.list[ind][0] == '#':
                myfile.list[ind:ind+1] = []
            else:
                print('found old and new inds, but old isn not commented out:')
                print(myfile.list[ind])


    if old_inds:
        myfile.save(pathin)




if __name__ == '__main__':
    import os, glob, rwkos
    ## #Undo using git
    ## git_root = '/home/ryan/git'
    ## dirs = rwkos.find_dirs(git_root)
    ## curdir = os.getcwd()
    ## for curdir in dirs:
    ##     root = os.path.join(git_root, curdir)
    ##     os.chdir(root)
    ##     os.system('git checkout .')

    ## os.chdir(curdir)

    import file_finder
    myfinder = file_finder.File_Finder('/home/ryan/git/', \
                                       extlist=['.py'], \
                                       skipdirs=['sympy'])
    pyfiles = myfinder.Find_All_Files()

    for curfile in pyfiles:
        fix_one_file(curfile)
