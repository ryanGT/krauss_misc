import delimited_file_utils

import glob
from numpy import array

files = glob.glob('email_update_grades_test*.csv')

good_labels = array(['Group Name','Content/Progress','Clarity','Writing','Apparent Effort','Overall Grade','Notes'])

passes = []
failures = []

for curfile in files:
    curarray = delimited_file_utils.open_delimited_with_sniffer_and_check(curfile)
    labels = curarray[0,:]
    data = curarray[1:,:]
    bool_vect = labels == good_labels
    test1 = bool_vect.all()
    test2 = data.shape == (9,7)
    if test1 and test2:
        passes.append(curfile)
    else:
        failures.append(curfile)

if len(failures) == 0:
    print('all tests pass')
else:
    print('passes:')
    for curfile in passes:
        print(curfile)
    print('-----------------------------')
    print('failures:')
    for curfile in failures:
        print(curfile)
    
