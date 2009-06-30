import os, re
import pytexutils

class txt_file(object):
    def readfile(self, pathin, strip=False, rstrip=True):
        return pytexutils.readfile(pathin, strip=strip, rstrip=rstrip)


    def writefile(self, pathin, listin=None, append=False):
        if listin is None:
            listin = self.list
        return pytexutils.writefile(pathin, listin, append=append)


    def save(self, pathout, append=False):
        return pytexutils.writefile(pathout, self.list, append=append)


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


    def find_next_non_comment(self, com_sym='#', start_ind=0):
        """Find the next line that doesn't start with a comment."""
        for x, line in enumerate(self[start_ind:]):
            if line[0] != com_sym:
                return x+start_ind
        return None
                


    def findall(self, pattern, forcestart=0, start_ind=0):
        return self._find(pattern, forcestart=forcestart, \
                          start_ind=start_ind)
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


    def replaceall(self, findpat, rep, forcestart=0):
        inds = self.findall(findpat, forcestart=forcestart)
        for ind in inds:
            linein = self[ind]
            temp = linein
            lineout = linein.replace(findpat, rep)
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


    def findnext(self, pattern, ind=0):
        return self._find(pattern, start_ind=ind, only_one=True)
    
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
        return self._find(pattern, regexp=True, match=match)
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


    def get_list(self, indlist):
        list_out = [self[ind] for ind in indlist]
        return txt_list(list_out)
    

default_map = ['findall', 'findallre', 'findprevious', \
               'findnext', 'replaceall', 'findnextblank', \
               'replaceallre', 'append','extend']

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
            

                                         


def dump(filename, listin):
    myfile = txt_file()
    myfile.writefile(filename, listin)

