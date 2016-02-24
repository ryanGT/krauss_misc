from filecmp import dircmp
def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print "diff_file %s found in %s and %s" % \
              (name, dcmp.left,dcmp.right)
    for key, sub_dcmp in dcmp.subdirs.iteritems():
        print(key)
        print_diff_files(sub_dcmp)


#a = '/Volumes/RYANSSD1/siue/classes/356'
#b = '/Volumes/IOMEGA/siue/classes/356'
a = '/Users/rkrauss/test1/'
b = '/Users/rkrauss/test2/'

dcmp = dircmp(a, b) 
#print_diff_files(dcmp) 
dcmp.report_full_closure()
