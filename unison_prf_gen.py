#!/usr/bin/env python
import os
from sync_dirs import quick_all, weekly_all, quick_only, personal, \
     ignore_list

import txt_mixin

all1 = quick_all + weekly_all

# quick_all means that it is included in all syncs, including weekly ones
quick_paths = quick_all + quick_only
## include myprefs
## #include usb_ignore

## root = /Users/kraussry/
## root = /Volumes/KRAUSS1/backup_unison
## path = scripts
unison_path = '/Users/kraussry/.unison/'

# ignore = Path {siue/admin/open_house}

               
class prf_generator(object):
    def __init__(self, filename, root1='/Users/kraussry/', \
                 root2='/Volumes/KRAUSS1/', \
                 root2_folder='', \
                 path_list=[]):
        self.filename = filename
        self.root1 = root1
        self.root2 = root2
        self.root2_folder = root2_folder
        self.path_list = path_list


    def build_list(self):
        mylist = ['include myprefs', '']
        out = mylist.append
        out('root = %s' % self.root1)
        if self.root2_folder:
            r2_path = os.path.join(self.root2, self.root2_folder)
        else:
            r2_path = self.root2
        out('root = %s' % r2_path)
        out('')
        
        for item in self.path_list:
            out('path = %s' % item)

        # append ignore paths
        out('')
        for item in ignore_list:
            curline = 'ignore = Path {%s}' % item
            out(curline)
            
        self.list = mylist


    def save(self):
        if not hasattr(self,'list'):
            self.build_list()
        pathout = os.path.join(unison_path, self.filename)
        txt_mixin.dump(pathout, self.list)


    def go(self):
        self.build_list()
        self.save()
        


if __name__ == '__main__':
    ## gen1 = prf_generator('KRAUSS1_daily.prf', \
    ##                      root1='/Users/kraussry/', \
    ##                      root2='/Volumes/KRAUSS1/', \
    ##                      root2_folder='backup_unison', \
    ##                      path_list=quick_all)
    ## gen1.go()

    ## gen2 = prf_generator('KRAUSS1_weekly.prf', \
    ##                      root1='/Users/kraussry/', \
    ##                      root2='/Volumes/KRAUSS1/', \
    ##                      root2_folder='backup_unison', \
    ##                      path_list=all1)
    ## gen2.go()

    ## gen3 = prf_generator('Rosewill_SSD_daily.prf', \
    ##                      root1='/Users/kraussry/', \
    ##                      root2='/Volumes/RYANSSD1', \
    ##                      root2_folder=None, \
    ##                      path_list=quick_all)
    ## gen3.go()

    ## gen4 = prf_generator('Rosewill_SSD_weekly.prf', \
    ##                      root1='/Users/kraussry/', \
    ##                      root2='/Volumes/RYANSSD1/', \
    ##                      root2_folder=None, \
    ##                      path_list=all1)
    ## gen4.go()
    #/gvsu_backup

    mytuples = [('KRAUSS1_%s.prf','/Volumes/KRAUSS1/','gvsu_backup'), \
                ('Backup_rwk_1_%s.prf','/Volumes/BACKUPRWK2/',None), \
                ('KRAUSSWDFAT_%s.prf','/Volumes/KraussWDFat/','gvsu_backup'), \
                ]

    for curtup in mytuples:
        pat = curtup[0]
        root2 = curtup[1]
        root2_folder = curtup[2]

        daily_name = pat % 'daily'
        daily_gen = prf_generator(daily_name, \
                                  root1='/Users/kraussry/', \
                                  root2=root2, \
                                  root2_folder=root2_folder, \
                                  path_list=quick_paths)
        daily_gen.go()

        daily_name = pat % 'personal'
        daily_gen = prf_generator(daily_name, \
                                  root1='/Users/kraussry/', \
                                  root2=root2, \
                                  root2_folder=root2_folder, \
                                  path_list=personal)
        daily_gen.go()

        weekly_name = pat % 'weekly'
        weekly_gen = prf_generator(weekly_name, \
                          root1='/Users/kraussry/', \
                          root2=root2, \
                          root2_folder=root2_folder, \
                          path_list=all1)
        weekly_gen.go()
