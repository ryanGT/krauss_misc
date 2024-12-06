import os, re
from krauss_misc import basic_file_ops
#from numpy import array, zeros, ones


class txt_file(object):
    def readfile(self, pathin, strip=False, rstrip=True):
        return basic_file_ops.readfile(pathin, strip=strip, rstrip=rstrip)


    def writefile(self, pathin, listin=None, append=False):
        if listin is None:
            listin = self.list
        return basic_file_ops.writefile(pathin, listin, append=append)


    def save(self, pathout, append=False):
        return basic_file_ops.writefile(pathout, self.list, append=append)


class txt_list(list):
    def _find(self, pattern, forcestart=0, start_ind=0, \
              only_one=False, regexp=False, match=False):
        linenums=[]
        if regexp:
            if type(pattern) == str:
                p=re.compile(pattern)
            else:
                #assume non-strings are already compiled
                p=pattern
                
        for x, line in enumerate(self[start_ind:]):
            if regexp:
                if match:
                    m=p.match(line)
                else:
                    m=p.search(line)
                if m:
                    linenums.append(x+start_ind)
            else:
                if match:
                    if line == pattern:
                        linenums.append(x+start_ind)
                else:
                    ind=line.find(pattern)
                    if forcestart:
                        if ind==0:
                            linenums.append(x+start_ind)
                    else:
                        if ind > -1:
                            linenums.append(x+start_ind)
            if linenums and only_one:
                break
        if only_one:
            if linenums:
                return linenums[0]
            else:
                return None
        else:
            return linenums


    def _find_boolvect(self, pattern, *args, **kwargs):
        """Just like _find, but return a boolvect of matching items
        rather than just the indices of matches."""
        from scipy import zeros
        inds = self._find(pattern, *args, **kwargs)
        N = len(self)
        bool_vect = zeros(N, dtype=bool)
        bool_vect[inds] = True
        return bool_vect
        

    def find(self, pattern, **kwargs):
        out = self._find(pattern, **kwargs)
        if out is None:
            return out
        if out == []:
            return None
        if len(out) > 1:
            print('found more than one match for ' + pattern)
        return out[0]


    def find_next_non_comment(self, com_sym='#', start_ind=0):
        """Find the next line that doesn't start with a comment."""
        for x, line in enumerate(self[start_ind:]):
            if line[0] != com_sym:
                return x+start_ind
        return None
                


    def findall(self, pattern, forcestart=0, start_ind=0, **kwargs):
        return self._find(pattern, forcestart=forcestart, \
                          start_ind=start_ind, **kwargs)
##         linenums=[]
##         for line,x in zip(self, range(len(self))):
##             ind=line.find(pattern)
##             if forcestart:
##                 if ind==0:
##                     linenums.append(x)
##             else:
##                 if ind >- 1:
##                     linenums.append(x)
##         return linenums


    def replaceall(self, findpat, rep, forcestart=0, \
                   callmanytimes=0):
        inds = self.findall(findpat, forcestart=forcestart)
        for ind in inds:
            linein = self[ind]
            temp = linein
            lineout = linein.replace(findpat, rep)
            #I don't think this makes sense.  For a recent case, I
            #wanted to replace Gth with Gth(s).  This causes an
            #endless loop.  What is wrong with just one replacement?
            if callmanytimes:
                while temp != lineout:
                    temp = lineout
                    lineout = lineout.replace(findpat, rep)
            self[ind] = lineout
            

    def findprevious(self, pattern, ind):
        inds = self.findall(pattern)
        filtlist = [item for item in inds if item < ind]
        if filtlist:
            return filtlist[-1]
        else:
            return None


    def findnext(self, pattern, ind=0, forcestart=0):
        return self._find(pattern, start_ind=ind, only_one=True, \
                          forcestart=forcestart)
    
##         inds = self.findall(pattern)
##         filtlist = [item for item in inds if item >= ind]
##         if filtlist:
##             return filtlist[0]
##         else:
##             return None


    def findnextre(self, pattern, ind=0, match=1):
        return self._find(pattern, start_ind=ind, \
                          regexp=True, only_one=True)


    def findnextblank(self, startind):
        for n, line in enumerate(self[startind:]):
            if not line:
                return n+startind
        return None


    def findallre(self, pattern, match=1, start_ind=0):
        """Use regular expression module re to find all lines with
        pattern.

        If match=1 or True, then a match is preformed, anchoring the
        search to the begining of each line.  match=0 or False calls
        re.search which matches pattern anywhere in the current line."""
        return self._find(pattern, regexp=True, match=match, \
                         start_ind=start_ind)
##         p=re.compile(pattern)
##         linenums=[]
##         for line,x in zip(self, range(len(self))):
##             if match:
##                 m=p.match(line)
##             else:
##                 m=p.search(line)
##             if m:
##                 linenums.append(x)
##         return linenums             


    def replaceallre(self, pattern, reppat):
        p = re.compile(pattern)
        for n, line in enumerate(self):
            line = p.sub(reppat, line)
            self[n] = line

            
    def find_before(self, pat1, pat2, usere=True, \
                    max_N=10, match=False, start_ind=0):
        inds = self.findallre(pat1, match=match, start_ind=start_ind)
        assert len(inds)==1, "Did not find exactly one match for the regular expression %s \n" % pat1 + \
               "len(inds)=%i" % len(inds)
        N1 = inds[0]
        if usere:
            inds2 = self.findallre(pat2, match=match)
        else:
            inds2 = self.findall(pat2)
        assert len(inds2) > 0, "Did not find %s in self.list" % pat2
        filt_inds = [item for item in inds2 if item < N1]
        assert len(filt_inds) > 0, "Did not find %s before %s" % (pat1, pat2)
        N2 = filt_inds[-1]
        assert N1-N2 < max_N, "Did not find %s within %i lines of %s" % (pat2, max_N, pat1)
        line = self[N2]
        return line, N2
        

    def replace_before(self, pat1, pat2, replace_pat, max_N=10, \
                       match=False, start_ind=0):
        """Search for pat1 in list, asserting that there is only one
        instance of it.  The search for the first instance of pat2
        before pat1.  Replace this instance of pat2 with replace_pat.
        pat1, pat2, and replace_pat are all regexps.  max_N refers to
        the maximumu line difference between pat1 and pat2.

        match refers to forcing pat1 and pat2 to be anchored to the
        beginning of a line.  start_ind refers to the first index of
        list to be used in searching for pat1."""
        line, N2 = self.find_before(pat1, pat2, usere=True, \
                                    max_N=max_N, match=match, \
                                    start_ind=start_ind)
        p = re.compile(pat2)
        lineout = p.sub(replace_pat, line)
        self[N2] = lineout


    def replace_line_before(self, pat1, oldline, newline, max_N=10, \
                            match=False, start_ind=0):
        line, N2 = self.find_before(pat1, oldline, usere=False, \
                                    max_N=max_N, match=match, \
                                    start_ind=start_ind)
        self[N2] = newline


    def is_blank(self, ind):
        test_line = self[ind]
        test_str = test_line.strip()
        return not bool(test_str)

    
    def delete_blanks_at_ind(self, ind):
        for i in range(5):
            if self.is_blank(ind):
                self.pop(ind)
            else:
                break    


    def one_blank_below(self, ind):
        """Ensure that there is exactly one blank line below ind.  This is
           used when inserting google drive links into markdown
           presentations, for example.

           But, if ind is the last line, just don't worry about it.
        """
        N = len(self)
        if ind >= N-1:
            # don't worry about it
            return
        if not self.is_blank(ind+1):
            self.insert(ind+1,'')
            # there should be no need to check ind+2, because we just
            # pushed a non-empty line down there
            return

        self.delete_blanks_at_ind(ind+2)


    def delete_blanks_above_ind(self, ind):
        """while self[ind-1] is blank, pop it and then decrement ind, but do
           this a maximum of 5 times"""
        for i in range(5):
           if self.is_blank(ind-1):
               self.pop(ind-1)
               ind -= 1
           else:
               break
           
        
    def one_blank_above(self, ind):
        """This is similar to self.one_blank_below, but it is slightly more
           complicated because deleting a line above shifts everything up."""
        if not self.is_blank(ind-1):
            self.insert(ind,'')
            # the original ind line just shifted down, so we need to
            # increment ind, but we should just exit because the non-blank
            # line that was above is not two lines up from the original ind
            return

        self.delete_blanks_above_ind(ind-1)


    def one_blank_above_and_below(self, ind):
        self.one_blank_below(ind)
        self.one_blank_above(ind)
        
        
    def get_list(self, indlist):
        list_out = [self[ind] for ind in indlist]
        return txt_list(list_out)


    def find_unique(self):
        temp = [1]*len(self)
        mydict = dict(zip(self, temp))
        return mydict.keys()

    def count(self, value):
        mycount = 0
        for item in self:
            if item == value:
                mycount += 1
        return mycount
        
    
class txt_list_lowercase(txt_list):
    def __init__(self, listin, *args, **kwargs):
        lower_list = [item.lower() for item in listin]
        txt_list.__init__(self, lower_list, *args, **kwargs)

                 
    
default_map = ['findall', 'findallre', 'findprevious', \
               'findnext', 'replaceall', 'findnextblank', \
               'replaceallre', 'append','extend', \
               'replace_before', 'replace_line_before', \
               '__delitem__','__len__','__delattr__', \
               '__getitem__','__setattr__', \
               '__setitem__',\
               ]
               #not py3 compatible:
               #'__getslice__','__delslice__','__setslice__', \



class txt_file_with_list(txt_file):
    """This class represents a text file that is read into self.list."""
    def append_file_to_list(self, pathin, strip=False, rstrip=True):
        newlist = self.readfile(pathin, strip=strip, rstrip=rstrip)
        self.list.extend(newlist)
        return self.list


    def refresh_list_map(self, list_map=None):
        """I had trouble with changing the list of an instance and not
        having this mapping work.  It seemed like it was still mapped
        from the empty initial list.  So, call this method if you
        reassign the list of an instance."""
        if list_map is None:
            list_map = self.list_map
        else:
            self.list_map = list_map
        for item in list_map:
            cur_func = getattr(self.list, item)
            setattr(self, item, cur_func)#map functions from self.list
                                         #to self to reduce typing
        

    def __init__(self, pathin=None, list_map=default_map):
        if list_map is None:
            list_map = default_map
        self.list = txt_list()
        self.pathin = pathin
        self.list_map = list_map
        if pathin is not None:
            if os.path.exists(pathin):
                self.append_file_to_list(pathin)
                self.folder, self.filename = os.path.split(pathin)
        self.refresh_list_map()
            


class delimited_txt_file(txt_file_with_list):
    def break_list(self):
        nested_list = []
        for line in self.list:
            curlist = line.split(self.delim)
            nested_list.append(curlist)
            
        self.nested_list = nested_list
        return self.nested_list
    
        
    def __init__(self, pathin=None, list_map=default_map, delim='\t',num_cols=None):
        from delimited_file_utils import open_delimited_with_sniffer_and_check
        txt_file_with_list.__init__(self, pathin, list_map=list_map)
        self.delim = delim
        self.break_list()#<-- eventually, this could probably be eliminated
        #self.array = array(self.nested_list)
        self.array = open_delimited_with_sniffer_and_check(pathin,num_cols=num_cols)#<-- new stuff
        

    def save(self, pathout, array=None, delim=None):
        if delim is None:
            delim = self.delim
        if array is None:
            array = self.array

        outlist = []
        
        for row in array:
            row_str = delim.join(row)
            outlist.append(row_str)
            

        dump(pathout, outlist)

             
def dump(filename, listin, append=False):
    myfile = txt_file()
    myfile.writefile(filename, listin, append=append)


def _row_to_spreadsheet_string(row, fmt='%s', delim='\t'):
    list_of_strs = [fmt % item for item in row]
    row_str = delim.join(list_of_strs)
    return row_str


def array_and_labels_to_spreadsheet_string(array, delim='\t', fmt='%s', \
                                           labels=[]):
    list_of_rows = [_row_to_spreadsheet_string(item, fmt=fmt, delim=delim) \
                    for item in array]
    if len(labels) > 0:
        label_row_str = _row_to_spreadsheet_string(labels, fmt='%s', delim=delim)
        list_of_rows = [label_row_str] + list_of_rows

    return list_of_rows

    
def dump_delimited(filename, array, delim='\t', fmt='%s', labels=[]):
    """Convert an array or a nested list to list of delimited row
    strings and then pass that list to the regular dump function."""
    list_of_rows = array_and_labels_to_spreadsheet_string(array, \
                                                          delim=delim, \
                                                          fmt=fmt, \
                                                          labels=labels)
    dump(filename, list_of_rows)


def read(filename):
    myfile = txt_file()
    out = myfile.readfile(filename)
    return out
