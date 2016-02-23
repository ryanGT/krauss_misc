#!/usr/bin/env python
import os
from sync_dirs import quick_all, weekly_all
import txt_mixin

all1 = quick_all + weekly_all

## include myprefs
## #include usb_ignore

## root = /Users/rkrauss/
## root = /Volumes/KRAUSS1/backup_unison
## path = scripts
unison_path = '/Users/rkrauss/.unison/'

class prf_generator(object):
    def __init__(self, filename, root1='/Users/rkrauss/', \
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
    gen1 = prf_generator('KRAUSS1_daily.prf', \
                         root1='/Users/rkrauss/', \
                         root2='/Volumes/KRAUSS1/', \
                         root2_folder='backup_unison', \
                         path_list=quick_all)
    gen1.go()

    gen2 = prf_generator('KRAUSS1_weekly.prf', \
                         root1='/Users/rkrauss/', \
                         root2='/Volumes/KRAUSS1/', \
                         root2_folder='backup_unison', \
                         path_list=all1)
    gen2.go()

    gen3 = prf_generator('Rosewill_SSD_daily.prf', \
                         root1='/Users/rkrauss/', \
                         root2='/Volumes/RYANSSD1', \
                         root2_folder=None, \
                         path_list=quick_all)
    gen3.go()

    gen4 = prf_generator('Rosewill_SSD_weekly.prf', \
                         root1='/Users/rkrauss/', \
                         root2='/Volumes/RYANSSD1/', \
                         root2_folder=None, \
                         path_list=all1)
    gen4.go()
