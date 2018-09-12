import csv, os
from numpy import array
from scipy import stats
"""I have been frustrated trying to open certain csv files and convert
them to numpy arrays.  If the nested lists don't all have the same
number of elements, things get messy.  I am trying to fix that and
find better info on where the problems are using the csv module.

The main function that does everything is called
open_delimited_with_sniffer_and_check."""

{'__module__': 'csv', 'lineterminator': '\r\n', 'skipinitialspace': False, 'quoting': 0, '_name': 'sniffed', 'delimiter': '\t', 'quotechar': '"', '__doc__': None, 'doublequote': False}

class tabdelim(csv.Dialect):
    # placeholders
    delimiter = '\t'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect('tabdelim', tabdelim)

class mycsv(csv.Dialect):
    # placeholders
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect('mycsv', mycsv)

encodings_to_try = ['latin-1','utf-16','utf-16-le','utf-16-be']

def sniff(pathin, bytes=1000):
    if not os.path.exists(pathin):
        return mycsv
    try:
        f = open(pathin,'r')#, encoding='utf-16')
        mystr = f.read(1000)
    except:
        N = len(encodings_to_try)
        for i in range(N):
            try:
                f = open(pathin,'r', encoding=encodings_to_try[i])
                mystr = f.read(1000)
                break
            except:
                pass
            
    mysniff = csv.Sniffer()
    mylist = mystr.split('\n')
    if mylist[0].find('\t') > -1:
        delim = '\t'
        dialect = tabdelim
    elif mylist[0].find(',') > -1:
        delim = ','
        dialect = mycsv
    else:
        try:
            dialect = mysniff.sniff(mystr)
        except:
            dialect = tabdelim#<-- sort of punting here, could be dangerous
    return dialect


def _open_delimited(pathin, dialect):
    try:
        reader = csv.reader(open(pathin,'r'), dialect)
        alllines = [row for row in reader]
    except:
        try:
            reader = csv.reader(open(pathin,'r', encoding='latin-1'), dialect)
            alllines = [row for row in reader]
        except:
            reader = csv.reader(open(pathin,'r', encoding='utf-16'), dialect)
            alllines = [row for row in reader]
            
    return alllines

    
def open_delimited_with_sniffer(pathin):
    dialect = sniff(pathin)
    alllines = _open_delimited(pathin, dialect)
    return alllines


def open_delimited_dialect(pathin, dialect=None, delim=None):
    """delim can be used to specify dialect.  Do not specifiy delim if
    you are also specifying dialect, since delim not equal to None
    overrides dialect."""
    if delim is not None:
        if delim == ',':
            dialect = mycsv
        elif delim == '\t':
            dialect = tabdelim
        else:
            raise(ValueError, "Not sure what to do with delimiter %s" % delim)
    alllines = _open_delimited(pathin, dialect)
    return alllines


def filter_empty_lines(nestedlist):
    listout = [item for item in nestedlist if item]
    return listout


def filter_if_first_item_empy(nestedlist):
    listout = [item for item in nestedlist if item[0]]
    return listout


def check_delimited_for_uniformity(nestedlist):
    items_per_row = [len(line) for line in nestedlist]
    items_array = array(items_per_row)
    mode, N_mode = stats.mstats.mode(items_array)
    N = len(items_array)
    if N == N_mode:
        return True
    else:
        print('mode = %s' % mode)
        print('---------------------')
        for i, row in enumerate(nestedlist):
            if len(row) != mode:
                print('bad row: i = %i, len = %i, %s' % (i, len(row), row))
    
    
def open_delimited_with_sniffer_and_check(pathin):
    list1 = open_delimited_with_sniffer(pathin)
    list2 = filter_empty_lines(list1)
    list3 = filter_if_first_item_empy(list2)
    test = check_delimited_for_uniformity(list3)
    assert test, "opening %s failed the uniformity check" % pathin
    return array(list3)


#def write_removing_numeric_quotes(data, labels, filepath):
    
