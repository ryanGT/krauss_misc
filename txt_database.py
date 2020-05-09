from numpy import *
import misc_utils
import numpy
import copy
import re
import txt_mixin, delimited_file_utils

from IPython.core.debugger import Pdb

def get_non_blanks(arrayin):
    inds = where(arrayin != '')
    if arrayin.ndim == 1:
        inds = inds[0]
    return arrayin[inds]


def label_to_attr_name(label):
    illegal_chars = [' ',':','/','\\','#','(',')',',','-','[',']','|','.','%']
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
        for attr, col_ind in self.col_attr_dict.items():
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


    def find_attr_re(self, repat):
        attr = None
    
        for item in self.attr_names:
            q = repat.search(item)
            if q is not None:
                attr = q.group()
                break
        return attr
    

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


    def _replace_commas_in_numbers(self,vect):
        mylist = vect.tolist()
        clean_list = [item.replace(',','') for item in mylist]
        return array(clean_list)


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
    
    def __next__(self):
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


class txt_database_from_file(txt_database):
    def __init__(self, filepath, skipcols=None):
        data, labels = _open_txt_file(filepath, delim=',')
        txt_database.__init__(self, data, labels)


        

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


# In order to check midterm grades, I want to find all quiz columns,
# output them next to each other, and calculate an average where each
# quiz is equally weighted.  Then I need to do the same for individual
# assignments and group project grades.  How do I do this?
#
# Big Idea:
#
# - in order to estimate their midterm grades, I need their grade on
# the midterm exam along with an estimate of their quiz ave, HW ave,
# and project ave

# - it seems like I need a column class
# - this will be messy
# - filter ungraded stuff
#   - create a list of graded cols
# - find quizzes first
# - find project grades next
# - whatever is left should be HW assignments
#   - unless they are surveys or something



def empty_strings_to_0(vect):
    """Replace all empty strings with '0' so that they can be
    converted to floats."""
    inds = where(vect=='')[0]
    vect[inds] = '0'
    return vect


def str_to_0(vect,str_in):
    """Replace all strings matching str_in with '0' so that they can
    be converted to floats."""
    inds = where(vect==str_in)[0]
    vect[inds] = '0'
    return vect


def needs_grading_to_0(vect):
    """Replace all empty strings with '0' so that they can be
    converted to floats."""
    inds = where(vect=='Needs Grading')[0]
    vect[inds] = '0'
    return vect

def in_progress_to_0(vect):
    vect = str_to_0(vect, 'In Progress')
    return vect


def replace_commas_in_numbers(vect):
    mylist = vect.tolist()
    clean_list = [item.replace(',','') for item in mylist]
    return array(clean_list)

p_average = re.compile("[Aa]verage.*")
p_pts = re.compile("Total_Pts_([0-9]+)_")
p_quiz = re.compile("^Quiz_([0-9]+)_")
p_quiz2 = re.compile("Quiz")
p_exam = re.compile("(Midterm_Grade|Exam_1|Exam_2).*")
p_group = re.compile("^Group")
#p_project = re.compile("[Pp]roject_.*")
p_project = re.compile("P(A|a)_*([0-9]+).*")
p_weighted_total = re.compile("^Weighted_Total_")
p_total = re.compile("^Total_")
p_survey = re.compile("[Ss]urvey_.*")
p_assign = re.compile("[LA]+(ssignment)*_*([0-9]+)_.*")
p_la = re.compile("[Ll]earning_[Aa]ctivity_([0-9]+)_.*")
p_extra_credit = re.compile("[Ee]xtra.*[Cc]redit")

col_pat_dict = {"average":p_average,\
                "quiz":p_quiz2, \
                "group_assign":p_group, \
                "project":p_project, \
                "weighted_total":p_weighted_total, \
                "total":p_total, \
                "assignment":p_assign, \
                "learning_activity":p_la, \
                "survey":p_survey, \
                "extra_credit":p_extra_credit, \
                "exam":p_exam, \
                }

pat_order_107 = ["average", \
                 "total", \
                 "weighted_total",\
                 "survey", \
                 "group_assign", \
                 "quiz", \
                 "project",\
                 "learning_activity",\
                 "assignment", \
                 "exam", \
                 "extra_credit"]

pat_order_445 = ["total","weighted_total",\
                 "survey", \
                 "quiz","project",\
                 "exam", \
                 "learning_activity",\
                 "assignment", \
                 "extra_credit"]



# next steps:
# - calc averages for columns (in bb_column class)
# - group grades by classification (in bb_grade_checker)
#   - only include graded columns
# - find appropriate totals for groups
# - average quizzes
# - find total average for hw and project groups

class bb_column(object):
    """This class exists to help me classify columns from a blackboard
    grade spreadsheet as either quiz, homework, group project,
    midterm, ... and help me filter out stuff that isn't yet grade and
    also determine appropriate totals and averages"""
    def clean_needs_grading(self):
        """Sometimes items are listed as Need Grading(####), i.e. they
        seem to have a suggested grade or something.  This seems to
        come from having one attempt graded and others ignored when
        students upload multiple times.  So, I need to replace Needs
        Grading(##) with the score in the paranthesis."""

        needs_str = "Needs Grading"
        pat = re.compile("Needs Grading *\\(([0-9.]+)\\)")
        
        for i, item in enumerate(self.list):
            q = pat.search(item)
            if q:
                self.list[i] = q.group(1)
                self.vector[i] = q.group(1)



    def clean_in_progress(self):
        """Sometimes items are listed as In Progress(####), i.e. they
        seem to have a suggested grade or one attempt has been graded
        or something.  This seems to come from having one attempt
        graded and others ignored when students upload multiple times.
        So, I need to replace Needs Grading(##) with the score in the
        paranthesis."""
    
        pat = re.compile("In Progress *\\(([0-9.]+)\\)")

        for i, item in enumerate(self.list):
            q = pat.search(item)
            if q:
                self.list[i] = q.group(1)
                self.vector[i] = q.group(1)

                
    def clean_grades(self):
        self.list = self.vector.tolist()
        self.clean_needs_grading()
        self.clean_in_progress()
        self.emptygrades = self.list.count('')
        self.needs_grading = self.list.count('Needs Grading')
        cleanvecta = empty_strings_to_0(self.vector)
        cleanvectb = replace_commas_in_numbers(cleanvecta)
        cleanvectc = needs_grading_to_0(cleanvectb)
        cleanvect = in_progress_to_0(cleanvectc)
        # you cannot convert 'Needs Grading' to a float;
        # but the length of the list cannot change if we are
        # going to output grades
        floatvect = cleanvect.astype(float)
        self.floatvect = floatvect
        
        q = p_pts.search(self.attr_name)

        percentages = None
        
        if q is not None:
            p_poss = float(q.group(1))
            if p_poss > 0:
                percentages = (self.floatvect/p_poss)*100
        else:
            p_poss = None
            
            
        ave = floatvect.mean()
        mymax = floatvect.max()
        mymin = floatvect.min()

        self.p_poss = p_poss
        self.ave = ave
        self.max = mymax
        self.min = mymin
        self.percentages = percentages


    def check_max(self):
        if self.p_poss is None:
            return True
        elif self.max > self.p_poss:
            return False
        else:
            return True
        

    def check_graded(self, N_tol=3, float_tol = 1.0e-4):
        graded = True
        if self.emptygrades > N_tol:
            graded = False
        elif self.ave < float_tol:
            graded = False
        elif self.max < float_tol:
            graded = False
        elif self.needs_grading > N_tol:
            graded = False

        self.graded = graded
        return graded
    

    def classify(self):
        self.classification = None

        exam = False
        if ("Midterm" in self.attr_name) or ("Exam" in self.attr_name):
            exam = True
            print("testing: %s" % self.attr_name)
            q_test = p_exam.search(self.attr_name)
            print("q_test = %s" % q_test)
            
        for key in self.pat_order:
            pattern = col_pat_dict[key]
            q = pattern.search(self.attr_name)

            if q is not None:
                self.classification = key
                break

        if exam:
            print("classification = %s" % self.classification)


        
    def __init__(self, attr_name, vect_in, N_tol=3, pat_order=pat_order_107):
        # N_tol refers to number of ungraded or empty grades in
        # a column to consider it not yet graded
        self.attr_name = attr_name
        self.vector = copy.copy(vect_in)
        self.clean_grades()                     
        self.check_graded(N_tol=N_tol)
        self.pat_order = pat_order
        self.classify()
        ## if self.classification != "extra_credit":
        ##     assert self.check_max(), "Max > possible: %s" % self.attr_name



    def __repr__(self):
        out_str = 'bb col: %s, class: %s' % (self.attr_name, \
                                             self.classification)
        return out_str



def get_short_col_name(colname):
    """Start with chopping off at _Total_Pts and then keep chopping"""
    chop_list = ["_Total_Pts", "_from_", "_From_", "_due","_Due"]
    outname = copy.copy(colname)

    for pat in chop_list:
        ind = outname.find(pat)
        if ind > -1:
            outname = outname[:ind]

    return outname


lpat = re.compile('[Ll]ast.*[Nn]ame')
fpat = re.compile('[Ff]irst.*[Nn]ame')

class class_list(txt_database_from_file):
    def __init__(self, *args, **kwargs):
        txt_database_from_file.__init__(self, *args, **kwargs)
        self.find_first_and_last_name()
        self.build_full_name()
        

    def find_first_and_last_name(self):
        lattr = self.find_attr_re(lpat)
        last_names = getattr(self, lattr)
        if lattr != 'last_names':
            self.last_names = last_names
        fattr = self.find_attr_re(fpat)
        first_names = getattr(self, fattr)
        if fattr != 'first_names':
            self.first_names = first_names
        

    def build_full_name(self):
        if not hasattr(self, 'fullnames'):
            fullnames = []
            for first, last in zip(self.first_names, self.last_names):
                cur_full = "%s, %s" % (last, first)
                fullnames.append(cur_full)
            self.fullnames = fullnames
            

class bb_grade_checker(txt_database_from_file):
    def __init__(self, *args, **kwargs):
        if 'pat_order' in kwargs:
            self.pat_order = kwargs['pat_order']
            kwargs.pop('pat_order', None)
        else:
            self.pat_order = pat_order_107

        if 'final' in kwargs:
            final = kwargs.pop('final')
        else:
            final = False

        txt_database_from_file.__init__(self, *args, **kwargs)
        if 'skipcols' in kwargs:
            skipcols = kwargs['skipcols']
        else:
            skipcols = None
        self._set_skip_cols(extraskipcols=skipcols)
        self.final=final


        
    def _set_skip_cols(self, extraskipcols=None):
        skipcols = ['Last_Name', \
                    'First_Name', \
                    'Username', \
                    'Student_ID', \
                    'Last_Access', \
                    'Availability', \
                    ]
        if extraskipcols is not None:
            skipcols += extraskipcols
        self.skipcols = skipcols
        self.p_pts = re.compile("Total_Pts_([0-9]+)_")
        

    def check_one_col(self, attr, verbosity=1):
        """check one bb column by pulling the Total_Pts out of the
        label and comparing it to the min, max, and mean for the
        column.  Care must be taken to handle empty grades and 'Needs
        Grading'"""
        myvect = getattr(self,attr)
        column = bb_column(attr, myvect, pat_order=self.pat_order)
        
        ## if verbosity > 0:
        ##     print('='*20)
        ##     print('attr: %s' % attr)
        ##     print('empty grades: %i' % emptygrades)
        ##     print('Needs Grading: %i' % ng)
        ##     if p_poss is None:
        ##         print('points possible not found')
        ##     else:
        ##         print('points possible: %0.5g' % p_poss)
        ##         print('ave: %0.5g' % ave)                
        ##     print('max: %0.5g' % mymax)
        ##     print('min: %0.5g' % mymin)

            
        ## return mydict


    def create_cols(self, verbosity=1, N_tol=3):
        cols = []
        for attr in self.attr_names:
            if attr not in self.skipcols:
                if verbosity > 0:
                    print('attr: %s' % attr)
                myvect = getattr(self,attr)
                column = bb_column(attr, myvect, N_tol=N_tol, \
                                   pat_order=self.pat_order)
                cols.append(column)

        self.columns = cols
                


    def get_graded_cols_one_classification(self, classification):
        matches = []

        for col in self.columns:
            if col.classification == classification:
                if self.final or col.graded:#assume all columns are
                                            #graded in a final grade check
                    matches.append(col)

        setattr(self, classification, matches)
        return matches


    def find_quiz_average_equal_weight(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave



    def find_quiz_average_weighted(self):
        self.get_graded_cols_one_classification("quiz")
        quiz_total = 0
        quiz_poss_total = 0

        for col in self.quiz:
            quiz_total += col.floatvect
            quiz_poss_total += col.p_poss

        self.quiz_total = quiz_total
        self.quiz_average = (quiz_total/quiz_poss_total)*100
        self.quiz_poss_total = quiz_poss_total
        return self.quiz_average


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols
        
        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)
        
        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.get_graded_cols_one_classification("project")
        
        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave

        
    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_column_with_start_match(self, pat, attr_set=None):
        """Find a column whose name starts with pat and set that
        column vector to self.attr_set"""
        if attr_set is None:
            attr_set = pat
        for attr in self.attr_names:
            if (attr not in self.skipcols) and (attr.find(pat) == 0):
                myvect = getattr(self, attr)
                col = bb_column(attr, myvect, pat_order=self.pat_order)
                setattr(self, attr_set, col)


    def find_exam_2(self):
        #Pdb().set_trace()
        self.find_column_with_start_match("Exam_2", "exam_2")
        

    ## def find_midterm(self):
    ##     for attr in self.attr_names:
    ##         if attr.find("Midterm_Exam") == 0:
    ##             myvect = getattr(self, attr)
    ##             self.midterm_exam = bb_column(attr, myvect)


    ## def find_midterm(self):
    ##     self.find_column_with_start_match("Midterm_Exam", "midterm_exam")

    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect
        denom = 0.7
        
        if self.has_project:
            self.midpoint += 0.3*self.project_ave
            denom = 1.0

        self.midpoint = self.midpoint/denom
        return self.midpoint

    
        


    def check_column_classification(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols
        
        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)
        
        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.get_graded_cols_one_classification("project")
        
        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave

        
    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_midterm(self):
        found = False
        for attr in self.attr_names:
            if (attr.find("Midterm_Grade") == 0) or (attr.find("Exam_1")==0):
                myvect = getattr(self, attr)
                self.midterm_exam = bb_column(attr, myvect, \
                                              pat_order=self.pat_order)
                found = True
                print('found')
                break

        if not found:
            print('did not find a midterm grade')

        
    def check_column_classification(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols
        
        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)
        
        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.has_project = True
        proj_cols = self.get_graded_cols_one_classification("project")
        if len(proj_cols) == 0:
            self.has_project = False
            return
        
        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave

        
    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    ## def find_midterm(self):
    ##     for attr in self.attr_names:
    ##         if attr.find("Midterm_Exam") == 0:
    ##             myvect = getattr(self, attr)
    ##             self.midterm_exam = bb_column(attr, myvect, \
    ##                                           pat_order=self.pat_order)


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        if self.has_project:
            mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Exam 1"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        if self.has_project:
            data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                                 midpoint_mat])
        else:
            data = column_stack([start_data,mat1,matq,midterm_mat, \
                                 midpoint_mat])            
        return data


    def check_column_classification(self, skip_list=[]):

        all_attrs = copy.copy(self.attr_names)
        
        for key in self.pat_order:
            cols = self.get_graded_cols_one_classification(key)

            if cols:
                print(key)
                print("-"*20)

            for col in cols:
                print(col.attr_name)
                all_attrs.remove(col.attr_name)

            print('')


        for item in skip_list:
            if item in all_attrs:
                all_attrs.remove(item)
                
                
        print('')
        print('Not used:')
        print('-'*20)

        for item in all_attrs:
            print(item)


        return all_attrs


class bb_107_final_grade_calculator(bb_grade_checker):
    def project_report_data(self, short=False):
        # The card game is the only project score for 107 in W17,
        # everything else is a group grade
        data = []
        labels = []


        for col in self.project:
            shortname = get_short_col_name(col.attr_name)
            labels.append(shortname)
            data.append(col.floatvect)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_group_average(self):
        self.get_graded_cols_one_classification("group_assign")

        group_total = copy.copy(self.group_assign[0].floatvect)
        group_poss_total = self.group_assign[0].p_poss

        for col in self.group_assign[1:]:
            group_total += col.floatvect
            group_poss_total += col.p_poss

        self.group_total = group_total
        self.group_ave = (group_total/group_poss_total)*100
        self.group_poss_total = group_poss_total
        return self.group_ave


    def group_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.group_assign:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        data.append(self.group_total)
        labels.append('Group Total (%i points possible)' % \
                               self.group_poss_total)

        data.append(self.group_ave)
        labels.append('Group Ave (%i points possible)' % \
                               self.group_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def attr_to_mat(self, attr, label):
        col = getattr(self, attr)
        vect = col.floatvect
        mylist = vect.astype(str).tolist()
        list_w_label = [label] + mylist
        mymat = atleast_2d(list_w_label).T
        return mymat


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        matg = self.group_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])

        # --> Get midterm and exam 2 into big_report
        
        if not hasattr(self,"midterm_exam"):
             self.find_midterm()

        midpoint_mat = self.attr_to_mat("midterm_exam", "Midterm Exam")
        
        if not hasattr(self, "exam_2"):
            self.find_exam_2()

        e2_mat = self.attr_to_mat("exam_2","Exam 2")
        
        ## self.estimate_grade_midpoint()
        ## midpoint_data = self.midpoint.tolist()
        ## midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        ## midpoint_mat = atleast_2d(midpoint2).T
        ## data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
        ##                      midpoint_mat])
        data = column_stack([start_data,mat1,mat2,matq,matg, \
                             midpoint_mat, e2_mat])
        return data

    # To do:
    # - check how I calculate the quiz average


class bb_107_final_grade_calculator_W20(bb_107_final_grade_calculator):
    def find_project_average(self):
        project_poss_total = 875+1100
        self.get_graded_cols_one_classification("project")

        project_total = copy.copy(self.project[0].floatvect)
        #project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            #project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave


    def _get_str_vect_for_attr_col(self, attr):
        col = getattr(self, attr)
        if isinstance(col, bb_column):
            mylist = col.floatvect.astype(str).tolist()
        else:
            mylist = col.astype(str).tolist()
        return mylist


    def build_report_col(self, attr, label):
        mylist = self._get_str_vect_for_attr_col(attr)
        outlist = [label] + mylist
        out_2D_col = atleast_2d(outlist).T
        return out_2D_col


    def calc_course_grade(self):
        self.course_grade = 0.2*self.hw_ave + \
                            0.1*self.quiz_average + \
                            0.4*self.exam_average + \
                            0.3*self.project_ave
        return self.course_grade
    
        
    def big_report(self, short=False):
        ### In the end, I need an average for each of the four areas on the
        ### syllabus:
        ###  - self.hw_ave
        ###  - self.project_ave
        ###  - self.quiz_average
        ###  - exam average
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])

        hw_mat = self.build_report_col("hw_ave", "HW Ave")
        proj_mat = self.build_report_col("project_ave", "Project Ave")
        quiz_mat = self.build_report_col("quiz_average", "Quiz Ave")
        
        midterm_mat = self.build_report_col("midterm_exam", "Midterm Exam")
        exam_2_mat = self.build_report_col("exam_2", "Exam 2")

        self.exam_average = (self.midterm_exam.floatvect + \
                             self.exam_2.floatvect)/2
        exam_ave_mat = self.build_report_col("exam_average", "Exam Average")

        self.calc_course_grade()
        course_grade_mat = self.build_report_col("course_grade", "Course Grade")
        
        data = column_stack([start_data,hw_mat,proj_mat, quiz_mat, \
                             midterm_mat, exam_2_mat, exam_ave_mat, \
                             course_grade_mat])
        return data


class bb_445_final_grade_helper(bb_107_final_grade_calculator):
    def __init__(self, *args, **kwargs):
        if 'pat_order' not in kwargs:
            kwargs['pat_order'] = pat_order_445
        bb_107_final_grade_calculator.__init__(self, *args, **kwargs)
        

    def find_project_average(self):

        for attr in self.attr_names:
            if attr.find(pat) == 0:
                myvect = getattr(self, attr)
                col = bb_column(attr, myvect, pat_order=self.pat_order)
                setattr(self, attr_set, col)


    def find_exam_2(self):
        #Pdb().set_trace()
        self.find_column_with_start_match("Exam_2", "exam_2")
        

    ## def find_midterm(self):
    ##     for attr in self.attr_names:
    ##         if attr.find("Midterm_Exam") == 0:
    ##             myvect = getattr(self, attr)
    ##             self.midterm_exam = bb_column(attr, myvect)


    def find_midterm(self):
        self.find_column_with_start_match("Midterm_Exam", "midterm_exam")


    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect
        denom = 0.7

        if self.has_project:
            self.midpoint += 0.3*self.project_ave
            denom = 1.0
            
        self.midpoint = self.midpoint/denom

        return self.midpoint
    
        
    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Midterm Exam"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                             midpoint_mat])
        return data


    def check_column_classification(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols
        
        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)
        
        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.get_graded_cols_one_classification("project")
        
        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave

        
    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_midterm(self):
        for attr in self.attr_names:
            if attr.find("Midterm_Exam") == 0:
                myvect = getattr(self, attr)
                self.midterm_exam = bb_column(attr, myvect, \
                                              pat_order=self.pat_order)


    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect + \
                        0.3*self.project_ave
        return self.midpoint
    
        
    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Midterm Exam"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                             midpoint_mat])
        return data


    def check_column_classification(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols
        
        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)
        
        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.get_graded_cols_one_classification("project")
        
        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave

        
    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_midterm(self):
        for attr in self.attr_names:
            if attr.find("Midterm_Exam") == 0:
                myvect = getattr(self, attr)
                self.midterm_exam = bb_column(attr, myvect, \
                                              pat_order=self.pat_order)


    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect + \
                        0.3*self.project_ave
        return self.midpoint
    
        
    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Midterm Exam"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                             midpoint_mat])
        return data


    def check_column_classification(self, skip_list=[]):

        all_attrs = copy.copy(self.attr_names)
        
        for key in self.pat_order:
            cols = self.get_graded_cols_one_classification(key)

            if cols:
                print(key)
                print("-"*20)

            for col in cols:
                print(col.attr_name)
                all_attrs.remove(col.attr_name)

            print('')


        for item in skip_list:
            if item in all_attrs:
                all_attrs.remove(item)
                
                
        print('')
        print('Not used:')
        print('-'*20)

        for item in all_attrs:
            print(item)


        return all_attrs


