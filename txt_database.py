from numpy import *
import misc_utils
import numpy
import copy

import txt_mixin, delimited_file_utils

from IPython.core.debugger import Pdb

def get_non_blanks(arrayin):
    inds = where(arrayin != '')
    if arrayin.ndim == 1:
        inds = inds[0]
    return arrayin[inds]


def label_to_attr_name(label):
    illegal_chars = [' ',':','/','\\','#','(',')',',','-']
    attr = label
    for char in illegal_chars:
        attr = attr.replace(char, '_')
    attr = attr.replace('__','_')
    while attr[-1] == '_':
        attr = attr[0:-1]
        
    return attr


def empty_data(data):
    """Check to see if data is an empty list or None."""
    if data is None:
        return True
    elif type(data) == list:
        if len(data) == 0:
            return True
            
    return False


def quote_strings(listin):
    listout = []

    for item_in in listin:
        try:
            item = float(item_in)
        except ValueError:
            item = item_in
        if type(item) in [str, unicode, numpy.string_]:
            value_out = '"%s"' % item
        else:
            value_out = item
        listout.append(value_out)

    return listout


def prep_data_for_save(data_in):
    #this is probably not the most efficient way to do this if data_in
    #is a numpy array of strings
    data_out = []
    for row in data_in:
        row_out = quote_strings(row)
        data_out.append(row_out)

    return data_out
    

class db_row(object):
    """This class will represent one row of a database and will be
    what is return when code iterates over a db."""
    def __init__(self, row_data, col_attr_dict):
        self.row_data = row_data
        self.col_attr_dict = col_attr_dict
        self.map_cols_to_attr()
        
        
    def map_cols_to_attr(self):
        """make each column of self.data an attribute of the db
        instance."""
        for attr, col_ind in self.col_attr_dict.iteritems():
            setattr(self, attr, self.row_data[col_ind])

    def __repr__(self):
        outstr = ''
        for key in self.col_attr_dict.keys():
            val = getattr(self, key)
            outstr += '%s: %s\n' % (key, val)

        return outstr

      
        

class txt_database(object):
    def search_attr_exact_match(self, attr, match):
        """retrieve attr using getattr(self, attr) and then find
        where(attr==match)[0].  Return the vector of boolean values
        for matching.  If match is an empty string, return a vector of
        all Trues."""
        vect = getattr(self, attr)
        if match == '':
            N = len(vect)
            bool_vect = ones(N, dtype=bool)
        else:
            bool_vect = vect==match
        return bool_vect


    def find_col_from_list(self, label_list, case_sensitive=False):
        """search through self.col_attr_dict to find a key in
        label_list.  When a key is found that is in label_list, return
        the corresponding column index.  If case_sensitive is False,
        use .lower() on the keys and the labels."""
        if not case_sensitive:
            search_list = [item.lower() for item in label_list]
        else:
            search_list = label_list

        for key, col_ind in self.col_attr_dict.iteritems():
            if not case_sensitive:
                key = key.lower()
            if key in search_list:
                return col_ind

        #if we got this far, the method did not find a column and will
        #return None
            

    
    def _empty_strings_to_0(self, vect):
        """Replace all empty strings with '0' so that they can be
        converted to floats."""
        inds = where(vect=='')[0]
        vect[inds] = '0'
        return vect


    def convert_cols_to_float(self, collabels):
        if type(collabels) == str:
            collabels = [collabels]
        for col in collabels:
            if hasattr(self, col):
                myvect = getattr(self, col)
                if type(myvect) == list:
                    myvect = array(myvect)
                myvect = self._empty_strings_to_0(myvect)
                myfloat = myvect.astype(float)
                setattr(self, col, myfloat)


    def convert_cols_to_int(self, collabels):
        self.convert_cols_to_float(collabels)
        for col in collabels:
            if hasattr(self, col):
                myfloat = getattr(self, col)
                myint = myfloat.astype(int)
                setattr(self, col, myint)



    def _col_labels_to_attr_names(self):
        """Replace any spaces or other illegal characters in the
        column labels to make them into legal attr names."""
        attr_names = []
        for label in self.labels:
            attr = label_to_attr_name(label)
            attr_names.append(attr)
        self.attr_names = attr_names
        self.label_attr_dict = dict(zip(self.attr_names, self.labels))
        self.attr_label_dict = dict(zip(self.labels, self.attr_names))
        N = len(self.attr_names)
        inds = range(N)
        self.col_attr_dict = dict(zip(self.attr_names, inds))


    def map_cols_to_attr(self):
        """make each column of self.data an attribute of the db
        instance."""
        for attr, label in zip(self.attr_names, self.labels):
            col_ind = self.col_inds[label]
            if len(self.data) > 0:
                setattr(self, attr, self.data[:,col_ind])


    def _sniff_delimiter(self, pathin):
        f = open(pathin,'r')
        first_row = f.readline()
        delim = None
        if first_row.find('\t') > -1:
            delim = '\t'
        elif first_row.find(',') > -1:
            delim = ','
        return delim


    def get_ind(self, key, key_label):
        key_col_ind = self.col_inds[key_label]
        key_col = self.data[:,key_col_ind]
        match_inds = where(key_col==key)[0]
        assert len(match_inds) > 0, "Did not find a match for " + str(key)
        assert len(match_inds) == 1, "Found more than one match for key " + str(key)
        row_ind = match_inds[0]
        return row_ind
    

    def get_row(self, key, key_label):
        row_ind = self.get_ind(key, key_label)
        return self.data[row_ind,:]


    def get_row_dict(self, key, key_label):
        row_data = self.get_row(key, key_label)
        mydict = dict(zip(self.labels, row_data))
        return mydict


    def __getitem__(self, index):
        row_data = self.data[index,:]
        #mydict = dict(zip(self.labels, row_data))
        #return mydict
        myrow = db_row(row_data, self.col_attr_dict)
        return myrow


    def search_for_key(self, key, key_label):
        key_col_ind = self.col_inds[key_label]
        if self.data is None:
            return []
        elif type(self.data) == list:
            if len(self.data) == 0:
                return []
        key_col = self.data[:,key_col_ind]
        match_inds = where(key_col==key)[0]
        return match_inds


    def update_one_row(self, key, key_label, update_dict):
        """Determine the correct row by search for key in the column
        whose labels is key_label.  Within that row, update the
        elements with entries from update_dict, where the keys of the
        dictionary are the column labels."""
        key_col_ind = self.col_inds[key_label]
        key_col = self.data[:,key_col_ind]
        match_inds = where(key_col==key)[0]
        assert len(match_inds) > 0, "Did not find a match for " + key
        assert len(match_inds) == 1, "Found more than one match for key " + key
        row_ind = match_inds[0]
        for key, val in update_dict.iteritems():
            key_col_ind = self.col_inds[key]
            self.data[row_ind, key_col_ind] = str(val)
            
            

    def new_row(self, key, key_label, new_dict):
        key_col_ind = self.col_inds[key_label]
        if empty_data(self.data):
            nc = len(self.labels)
        else:
            key_col = self.data[:,key_col_ind]
            match_inds = where(key_col==key)[0]
            assert len(match_inds) == 0, "Attempting to add a new row with a key that already exists: " + str(key)
            nr, nc = self.data.shape
            
        new_list = ['']*nc
        for key, val in new_dict.iteritems():
            key_col_ind = self.col_inds[key]
            new_list[key_col_ind] = str(val)

        new_row = array([new_list])
        if empty_data(self.data):
            self.data = new_row
        else:
            self.data = numpy.append(self.data, new_row, axis=0)


    def append_row_sorted(self, new_row):
        """Append row to self.data, assuming row is sorted in the same
        order as the existing data."""
        if len(self.data) == 0:
            self.data = numpy.atleast_2d(new_row)
        else:
            new2d = numpy.atleast_2d(new_row)
            self.data = numpy.append(self.data, new2d, axis=0)
        

    def add_new_column(self, col_data, label):
        new_data = column_stack([self.data,col_data])
        new_labels = numpy.append(self.labels, label)
        self.data = new_data
        self.labels = new_labels
        nr, nc = new_data.shape
        new_col_num = nc - 1
        attr = label_to_attr_name(label)
        self.attr_names.append(attr)
        setattr(self, attr, col_data)
        self.label_attr_dict[attr] = label
        self.col_attr_dict[attr] = new_col_num
        

        
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
        self.N_cols = len(self.labels)
        inds = range(self.N_cols)
        self.col_inds = dict(zip(self.labels, inds))
        self._col_labels_to_attr_names()
        self.next_ind = -1
        try:
            self.map_cols_to_attr()
        except:
            pass


    def __iter__(self):
        return self
    
    def next(self):
        self.next_ind += 1
        nr, nc = self.data.shape

        if self.next_ind >= nr:
            raise StopIteration
        else:
            
            return self[self.next_ind]
        

    def save(self, pathout, delim='\t'):
        """I need to add an intermediate step to quote strings for csv
        compliance, i.e. 'this is one really, really, long cell with
        commas.'"""
        ## data_out = prep_data_for_save(self.data)
        ## misc_utils.dump_matrix(pathout, data_out, self.labels, \
        ##                        fmt='%s', delim=delim)
        quoted_labels = ['"%s"' % item for item in self.labels]
        txt_mixin.dump_delimited(pathout,self.data,delim=delim, \
                                 labels=quoted_labels)


    def filter(self, boolvect):
        filt_data = copy.copy(self.data[boolvect])
        new_db = txt_database(filt_data, self.labels)
        return new_db


    def get_data_subset(self, key_label, match_keys):
        """search through the column whose label is key_label and find
        the entries that match match_keys.  Return a db that contains
        the subset of data that corresponds to those rows."""
        row_inds = []

        for key in match_keys:
            ind = self.get_ind(key, key_label)
            row_inds.append(ind)

        data = self.data[row_inds,:]
        new_db = txt_database(data, self.labels)
        return new_db


    def get_attr_by_label(self, label):
        attr_name = label_to_attr_name(label)
        if hasattr(self, attr_name):
            vect = getattr(self, attr_name)
            return vect
        else:
            raise ValueError('could not find column with this label: %s' % \
                             label)


    def get_matrix_from_label_list(self, labels):
        out = None
        for label in labels:
            attr = label_to_attr_name(label)
            col_ind = self.col_attr_dict[attr]
            cur_data = self.data[:,col_ind]
            if out is not None:
                out = column_stack([out, cur_data])
            else:
                out = cur_data

        return out


        

def _open_txt_file(pathin, delim='\t'):
    #import pdb
    #pdb.set_trace()
    #myfile = txt_mixin.delimited_txt_file(pathin, delim=delim)
    #alldata = loadtxt(pathin,dtype=str,delimiter=delim)
    #alldata = myfile.array
    alldata = delimited_file_utils.open_delimited_with_sniffer_and_check(pathin)
    labels = alldata[0,:]
    data = alldata[1:]
    return data, labels


def db_from_file(pathin, delim='\t'):
    data, labels = _open_txt_file(pathin, delim)
    mydb = txt_database(data, labels)
    return mydb
                       
