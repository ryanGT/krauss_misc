import os, rwkos

filesep = os.path.sep

src_base = '/Users/rkrauss'

def check_src(src_in):
    assert src_in.find(src_base) == 0, 'bad src: %s' % src_in
    
def check_dst(dst_in):
    assert dst_in.find('/Volumes/') == 0, 'bad dst: %s' % dst_in
    
    
def rsync_one(src, dst, flags=['-av']):
    check_src(src)
    check_dst(dst)
    flag_str = ' '.join(flags)
    cmd = 'rsync %s %s %s' % (src, dst, flags)
    os.system(cmd

              
class rsync_runner(object):
    def __init__(self, src_root, dst_root, dst_folder='', relpaths=[]):
        self.src_root = os.path.expanduser(src_root)
        check_src(self.src_root)
        self.dst_root = dst_root
        check_dst(self.dst_root)
        self.dst_folder = dst_folder
        self.relpaths = relpaths


    def make_dst_dirs(self):
        if self.dst_folder:
            self.dst_path = os.path.join(self.dst_root, self.dst_folder)
        else:
            self.dst_path = self.dst_root

        rwkos.make_dirs_recrusive(self.dst_path)

        for item in self.relpaths:
            # - if the src is a file, pop the filename
            # - make the dest folders recursively

            #####################
            ##if item.find(filesep) > -1:
            ##    # - do nothing if item doesn't contain a filesep
            #####################
            
            #recursively make folders
            src_path = os.path.join(self.src_root, item)
            cur_dest = os.path.join(self.dst_path, item)
            if os.path.isfile(src_path):
                #this is a file path, pop the file name to get the dir path
                cur_dest, cur_file = os.path.split(cur_dest)
                
            #make the directory structure if it doesn't exist
            if not os.path.exists(cur_dest):
                rwkos.make_dirs_recrusive(cur_dest)
            
