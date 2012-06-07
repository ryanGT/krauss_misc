from numpy import *
import misc_utils

class txt_database(object):
    def _empty_strings_to_0(self, vect):
        """Replace all empty strings with '0' so that they can be
        converted to floats."""
        inds = where(vect=='')[0]
        vect[inds] = '0'
        return vect


    def convert_cols_to_float(self, collabels):
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
            
            

    def __init__(self, pathin, delim='\t'):
        data = loadtxt(pathin,dtype=str,delimiter=delim)
        self.labels = data[0,:]
        self.data = data[1:,:]
        self.N_cols = len(self.labels)
        inds = range(self.N_cols)
        self.col_inds = dict(zip(self.labels, inds))
        self._col_labels_to_attr_names()
        self.map_cols_to_attr()


    def save(self, pathout, delim='\t'):
        misc_utils.dump_matrix(pathout, self.data, self.labels, \
                               fmt='%s', delim=delim)
