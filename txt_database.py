from numpy import *
import misc_utils
import numpy
import copy

import txt_mixin

#from IPython.core.debugger import Pdb

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
        illegal_chars = [' ',':','/','\\']
        attr_names = []
        for label in self.labels:
            attr = label
            for char in illegal_chars:
                attr = attr.replace(char, '_')
            attr_names.append(attr)
        self.attr_names = attr_names
        self.label_attr_dict = dict(zip(self.attr_names, self.labels))
        N = len(self.attr_names)
        inds = range(N)
        self.col_attr_dict = dict(zip(self.attr_names, inds))


    def map_cols_to_attr(self):
        """make each column of self.data an attribute of the db
        instance."""
        for attr, label in zip(self.attr_names, self.labels):
            col_ind = self.col_inds[label]
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
            
            

    def add_new_row(self, key, key_label, new_dict):
        key_col_ind = self.col_inds[key_label]
        key_col = self.data[:,key_col_ind]
        match_inds = where(key_col==key)[0]
        assert len(match_inds) == 0, "Attempting to add a new row with a key that already exists: " + str(key)
        nr, nc = self.data.shape
        new_list = ['']*nc
        for key, val in new_dict.iteritems():
            key_col_ind = self.col_inds[key]
            new_list[key_col_ind] = str(val)
            
        new_row = array([new_list])
        self.data = numpy.append(self.data, new_row, axis=0)
        
        
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
        self.N_cols = len(self.labels)
        inds = range(self.N_cols)
        self.col_inds = dict(zip(self.labels, inds))
        self._col_labels_to_attr_names()
        self.map_cols_to_attr()


    def save(self, pathout, delim='\t'):
        misc_utils.dump_matrix(pathout, self.data, self.labels, \
                               fmt='%s', delim=delim)



    def filter(self, boolvect):
        filt_data = copy.copy(self.data[boolvect])
        new_db = txt_database(filt_data, self.labels)
        return new_db
            
        

def _open_txt_file(pathin, delim='\t'):
    import pdb
    pdb.set_trace()
    myfile = txt_mixin.delimited_txt_file(pathin, delim=delim)
    #alldata = loadtxt(pathin,dtype=str,delimiter=delim)
    alldata = myfile.array
    labels = alldata[0,:]
    data = alldata[1:]
    return data, labels


def db_from_file(pathin, delim='\t'):
    data, labels = _open_txt_file(pathin, delim)
    mydb = txt_database(data, labels)
    return mydb
                       
