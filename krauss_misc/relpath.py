#!/usr/bin/python
#
# relpath.py
# R.Barran 30/08/2004

import os

def relpath(target, base=os.curdir, checkpaths=False):
    """
    Return a relative path to the target from either the current dir
    or an optional base dir.  Base can be a directory specified either
    as absolute or relative to current dir.
    """
    if checkpaths:
        if not os.path.exists(target):
            raise OSError('Target does not exist: '+target)

        if not os.path.isdir(base):
            raise OSError('Base is not a directory or does not exist: '+base)
    if target == base:
        return '.'
    absbase = os.path.abspath(base)
    # this should be generalized later
    # - I am not sure what problem this fixed, but it is causing issues now
    ## if absbase.find("Google Drive/Teaching/345_F19") > -1:
    ##     absbase = absbase.replace("Google Drive/Teaching/345_F19","345_F19")
    base_list = (absbase.split(os.sep))
    test=base_list.pop()
    if test != '':
        base_list.append(test)
    target_list = (os.path.abspath(target)).split(os.sep)
    if base_list == target_list:
        return ''

    # On the windows platform the target may be on a completely different drive from the base.
    if os.name in ['nt','dos','os2'] and base_list[0].upper() != target_list[0].upper():
        raise OSError('Target is on a different drive to base. Target: '+target_list[0].upper()+', base: '+base_list[0].upper())

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] != target_list[i]: break
    else:
        # If we broke out of the loop, i is pointing to the first differing path elements.
        # If we didn't break out of the loop, i is pointing to identical path elements.
        # Increment i so that in all cases it points to the first differing path elements.
        i+=1
#--------------------------------------------------
#     print "num unsed= " + str((len(base_list)-i))
#     print "i= " + str(i)
#     print "len(base_list)= " + str(len(base_list))
#-------------------------------------------------- 
    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)
