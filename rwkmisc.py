# rwk misc module

import scipy, copy
import time
import os, glob, re, sys

#from  IPython.Debugger import Pdb
#mytrace=Pdb().set_trace

import cPickle

def get_date_str():
    date_str = time.strftime('%m_%d_%y')
    return date_str

def clean_list(listin):
    """Remove blank entries from the start and end of the list."""
    listout = copy.copy(listin)
    while not listout[0]:
        listout.pop(0)
    while not listout[-1]:
        listout.pop()
    return listout

def clean_list_regexp(listin, pat='^[ ,]*$'):
    listout = copy.copy(listin)
    p = re.compile(pat)
    while p.match(listout[0]):
        listout.pop(0)
    while p.match(listout[-1]):
        listout.pop()
    return listout
                       
    
def RegExpPop(listin, pat, returnq=False, multiline=False):
    if multiline:
        mystr = '\n'.join(listin)
        p = re.compile(pat, flags=re.DOTALL)
        q = p.search(mystr)
        if q:
            out = q.group()
            newstr = p.sub('',mystr)
            listin = newstr.split('\n')
    else:
        p = re.compile(pat)
        out = None
        for n, item in enumerate(listin):
            q = p.search(item)
            if q:
                out = listin.pop(n)
                break
    if returnq:
        return q
    else:
        return out


def PrintToScreen(listin, globals):
    if type(listin)==str:
        listin=[listin]
    for item in listin:
        print(item+'=%s'%eval(item, globals))

    
def SavePickle(mydict, filepath, protocol=2):
    """Dump dictionary mydict to a Pickle file filepath using cPickle,
    protocol=2."""
    mypkl = open(filepath,'wb')
    cPickle.dump(mydict, mypkl, protocol=protocol)
    mypkl.close()


def LoadPickle(filepath):
    mypkl = open(filepath,'rb')
    mydict = cPickle.load(mypkl)
    mypkl.close()
    return mydict


def load_from_pickle(filename, key):
    mydict = LoadPickle(filename)
    return mydict[key]


def myglob(pattern, folder=None):
    if folder is not None:
        totalpattern = os.path.join(folder, pattern)
    else:
        totalpattern = pattern
    myfiles = glob.glob(totalpattern)
    if folder is not None:
        outnames = []
        for item in myfiles:
            fout, name = os.path.split(item)
            outnames.append(name)
    else:
        outnames = myfiles
    return outnames
        

class rwkstr(str):
    def findall(self, pattern):
        inds=[]
        remainingstr=copy.deepcopy(self)
        donestr=''
        while remainingstr.find(pattern)>-1:
            nextind=remainingstr.find(pattern)
            absind=nextind+len(donestr)
            inds.append(absind)
            donestr+=remainingstr[0:nextind+1]
            remainingstr=remainingstr[nextind+1:]
        return inds

    def replace(self,old,new,startind=0,maxreplace=-1):
#        print('in rwk replace')
        if old==new:
            return rwkstr(self)
        else:
            if startind>0:
                prestr=self[0:startind]
                rest=self[startind:]
                outstr=rest.replace(old,new,maxreplace=maxreplace)
                outstr=prestr+outstr
                return rwkstr(outstr)
            else:
                return rwkstr(str.replace(self,old,new,maxreplace))
    
    def __getslice__(self,si,ei):
#        print('in rwkstr getslice')
        return rwkstr(str.__getslice__(self,si,ei))

    def afterlast(self,pattern):
        ind=self.rfind(pattern)
        if ind>-1:
            firstpart=self[0:ind]
            lastpart=self[ind+len(pattern):]
            return firstpart,lastpart
        else:
            return self, ''

    def beforefirst(self,pattern,startind=0):
        ind=self.find(pattern,startind)
        if ind>-1:
            firstpart=self[0:ind]
            lastpart=self[ind+len(pattern):]
            return rwkstr(firstpart), rwkstr(lastpart)
        else:
            return self,''

    def contains(self,substr):
        return self.find(substr)!=-1
        
class symstr(rwkstr):
    def containsoperators(self,oplist=['*','+','-','/','**']):
        for co in oplist:
            if self.find(co)>-1:
                return True
                break
        else:
            return False

    def __addparen__(self,oplist=['*','+','-','/','**']):
        if self.containsoperators(oplist):
            return '('+self.__str__()+')'
        else:
            return self.__str__()

    def __add__(self,other):
        return symstr(self.__str__()+'+'+str(other))

    def __sub__(self,other):
        myops=['+','-']
        if not type(other)==symstr:
            other=symstr(other)
        return symstr(self.__str__()+'-'+other.__addparen__(myops))

    def __mul__(self,other):
        myops=['+','-']
        if not type(other)==symstr:
            other=symstr(other)
        return symstr(self.__addparen__(myops)+'*'+other.__addparen__(myops))

#    def __pow__(self,other):
#        return symstr(self+'^'+symstr(other).__addparen__())
    
    def __rmul__(self,other):
        myops=['+','-']
        if not type(other)==symstr:
            other=symstr(other)
        return symstr(other.__addparen__(myops)+'*'+self.__addparen__(myops))

    def __div__(self,other):
#        Pdb().set_trace()
        myops=['+','-']
        if not type(other)==symstr:
            other=symstr(other)
        return symstr(self.__addparen__(myops)+'/'+other.__addparen__())

    def __rdiv__(self,other):
        return symstr(other).__div__(self)

    def __rtruediv__(self,other):
        return self.__rdiv__(other)

    def __truediv__(self,other):
        return self.__div__(other)

    def __pow__(self,other):
        if not type(other)==symstr:
            other=symstr(other)
        return symstr(self.__addparen__()+'**'+other.__addparen__())

    def __neg__(self):
        return symstr('-'+self)


#def fullfile(path,file): #concatinate file strings intelligently
#    tempout=path+'\\'+file
#    temp2=tempout.replace('\\\\','\\')
#    while temp2!=tempout:
#        tempout=temp2
#        temp2=tempout.replace('\\\\','\\')

#    fileout=tempout
#    return tempout

class dictobject:
    def __init__(self,**kwargs):
        for key,value in kwargs.iteritems():
            setattr(self,key,value)

def SortLists(sortbylist,otherlists,reverse=False):
    """This function sorts lists similar to each list being a column
    of data in a spreadsheet program and choosing one column to sort
    by.

    The sortbylist is the column or list that you wish to sort by and
    otherlists is a list of the other lists or columns to sort.
    
    Reverse is passed to the sort method of sortbylist."""

    newlist=sortbylist[:]
    newlist.sort(reverse=reverse)
    bigoutlist=[]
    for list in otherlists:
        curlist=[]
        for curitem in newlist:
            ind=sortbylist.index(curitem)
            curlist.append(list[ind])
        bigoutlist.append(curlist)
    return (newlist,)+tuple(bigoutlist)

def transposed(lists):
   if not lists: return []
   return map(lambda *row: list(row), *lists)

def rwkWriteArray(file, array, append=0):  #open or create file and append or write array to it
    if append:
        f=open(file,'a')
    else:
        f=open(file,'w')
    for curline in array:
        f.write(curline)
    f.close()

def mydirfilter(pathin,ignoredirs):
    """pathin is assumed to be a path to a directory
    this function returns true if the last folder
    is not in the list of ignoredirs"""
    temproot, curdir=os.path.split(pathin)
    return curdir not in ignoredirs

def rwkFileSearchRecursive(pattern,root,outpath="",ignoredirs=[]):
    """Starting in root, walk down through the 
    file structure searching for pattern.  The 
    results are returned as a list of full paths.
    
    If outpath is specified, the output is also 
    written to it as an ASCII text file."""

    topdirs=glob.glob(os.path.join(root,'*'))
    topdirs=[item for item in topdirs if os.path.isdir(item)]
    topdirs=[item for item in topdirs if mydirfilter(item,ignoredirs)]
    allpaths=[]
    rootpat=os.path.join(root,pattern)
    rootfiles=glob.glob(rootpat)
    allpaths.extend(rootfiles)
    for curroot in topdirs:
        rootpat=os.path.join(curroot,pattern)
        rootfiles=glob.glob(rootpat)
        allpaths.extend(rootfiles)
        for root, dirs, files in os.walk(curroot):
            for name in dirs:
                curpath=os.path.join(root,name)
                print('searching:'+curpath)
                curpat=os.path.join(curpath,pattern)
                curfiles=glob.glob(curpat)
                allpaths.extend(curfiles)
    
    if outpath:
        rwkWriteArray(outpath,allpaths)

    return allpaths



def rwkFileSearch(pattern,searchdir="",outfile="",append=0): 
    """Search for pattern in searchdir without recursing into
    the directory (does not walk the directory tree).
    
    Returns files found as a list of filenames (not full paths).
    
    If outfile is specified, the results are also written to
    it (or appended) as a text file."""

#    import glob
#    import os
    
#    curdir=os.getcwd()
#    if len(searchdir)>0:
#        os.chdir(searchdir)
        

    #--------------------------------------------------
    # print 'pattern='+pattern
    # print 'curdir='+os.getcwd()
    #-------------------------------------------------- 
    curpat=os.path.join(searchdir,pattern)
    texfiles=glob.glob(curpat)
    #--------------------------------------------------
    # print 'filelist:'
    #-------------------------------------------------- 
    if len(outfile)>0:
        filestoprint=[]
        for k,curfile in enumerate(texfiles):
            filestoprint.append(curfile + '\n')

        rwkWriteArray(outfile,filestoprint,append)


#    os.chdir(curdir)
    return texfiles

def mycomp(strin, pattern, exact=False):
    """check pattern against strin.  If exact, then retrun
    pattern==strin, else return strin.find(pattern)>-1."""
    if exact:
        return bool(strin==pattern)
    else:
        return bool(strin.find(pattern)>-1)

def searchlist(listin, str2find, exact=False, casesense=False):
    """search for str2find in listin, return first index containing
    str2find, or -1 if it is not found.

    If exact is False, return the first index that contains str2find,
    otherwise require item == str2find for item in listin.

    casesense calls lower() on str2find and the items of listin."""
    indout=-1
    if not casesense:
        str2find=str2find.lower()
    for k, curstr in enumerate(listin):
        if not casesense:
            curstr=curstr.lower()
        if mycomp(curstr, str2find, exact=exact):
            indout=k
            break
    return indout

def my_import(name):
    folder, modname = os.path.split(name)
    if folder:
        if folder not in sys.path:
            sys.path.append(folder)
    mod = __import__(modname)
    components = modname.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def reverse( x ):
#    Pdb().set_trace()
    if hasattr(x,'tolist'):
        return scipy.array(reverse(x.tolist()))
    l2 = len(x)/2
    if l2:
        return reverse(x[l2:]) + reverse(x[:l2])
    else:
        return x

def null(A, eps=1e-10):
    u, s, vh = scipy.linalg.svd(A)
    null_mask = (s <= eps)
    null_space = scipy.compress(null_mask, vh, axis=0) 
    return scipy.transpose(scipy.conj(null_space)) 

def colwise(matin,makecopy=1):
#    t1=time.time()
    if makecopy:
        tempmat=copy.deepcopy(matin)
    else:
        tempmat=matin
#    t2=time.time()
#    print('copy time='+str(t2-t1))
    matout=scipy.atleast_2d(tempmat)
    myshape=scipy.shape(matout)
    if myshape[0]<myshape[1]:
        matout=scipy.transpose(matout)
    return matout

def rowwise(matin,makecopy=1):
#    t1=time.time()
    if makecopy:
        tempmat=copy.deepcopy(matin)
    else:
        tempmat=matin
#    t2=time.time()
#    print('copy time='+str(t2-t1))
    matout=scipy.atleast_2d(tempmat)
    myshape=scipy.shape(matout)
    if myshape[0]>myshape[1]:
        matout=scipy.transpose(matout)
    return matout

#def __printent(ent, eps=1e-14,bigthresh=10000,littlethresh=1e-5,width=8):
#    """Assumes only real input and is meant to be called by other functions like printent."""
#    if abs(ent)>bigthresh or ans(ent)<littlethresh:
#        fmt='%0.'+str(width-4)+'e'
#    else:
#        fmt='%'+str(width)+'g'
#    if eps is not None and abs(ent)<eps:
#        return '0'
#    else:
#        return fmt%ent

                    

#def PrettyMat(mat,eps=1e-14):
#    imat=imag(mat)
#    rmat=real(mat)
#    if rmat.any() and imat.any():
#        width=6
#    else:
#        width=8
#    for row in mat:
#        rowstr='['
#        for ent in row:
#            if imag(ent):
#                rstr=__printent(real(ent),width=width)



def prettymat(mat,fmt='%0.5g',eps=1e-14):
#        pdb.set_trace()
        if fmt[0]=='%':
            ifmt='%+'+fmt[1:]
        else:
            ifmt='%+'+fmt
            fmt='%'+fmt
        nc=scipy.shape(mat)[1]
#        print('[')
        outstr='['
#        fmtstr=fmt +(nc-1)*(' & ' +fmt)+'\\\\'
        for currow in mat.tolist():
#            curtuple=tuple(currow)
#            rowstr=fmtstr%curtuple
            rowstr='['
            for x,ent in enumerate(currow):
                if abs(scipy.real(ent))>eps:
                    realstr=fmt%scipy.real(ent)
                else:
                    realstr='0'
                if abs(scipy.imag(ent))>eps:
                    imagstr=ifmt%scipy.imag(ent)+'j'
                else:
                    imagstr=''
                rowstr+=realstr+imagstr
                if x<(len(currow)-1):
                    rowstr+=', '
                if x==(len(currow)-1):
                    rowstr+='],\n'
            outstr+=rowstr
        if outstr[-1]=='\n':
            outstr=outstr[0:-1]
        outstr+=']'
        print(outstr)
#        return outstr

def RREFscaled(mymat):
#    Pdb().set_trace()
    scalevect=scipy.amax(abs(mymat),1)
    scaledrows=[]
    for sf,row in zip(scalevect,mymat):
        row=row/sf
        scaledrows.append(row)
    scaledmat=scipy.vstack(scaledrows)
#    scaledmat=mymat
    nc=scipy.shape(scaledmat)[1]
    nr=scipy.shape(scaledmat)[0]
    for j in range(nr-1):
#        print('=====================')
#        print('j='+str(j))
        pivrow=scipy.argmax(abs(scaledmat[j:-1,j]))
        pivrow=pivrow+j
#        print('pivrow='+str(pivrow))
        if pivrow!=j:
            temprow=copy.copy(scaledmat[j,:])
            scaledmat[j,:]=scaledmat[pivrow,:]
            scaledmat[pivrow,:]=temprow
#        Pdb().set_trace()
        for i in range(j+1,nr):
#            print('i='+str(i))
            scaledmat[i,:]-=scaledmat[j,:]*(scaledmat[i,j]/scaledmat[j,j])
    return scaledmat, scalevect

def ColSwap(matin,c1,c2):
    tempcol=copy.deepcopy(matin[:,c1])
    matin[:,c1]=matin[:,c2]
    matin[:,c2]=tempcol
    return matin

def RowSwap(matin,r1,r2):
#    pdb.set_trace()
    temprow=scipy.zeros((1,scipy.shape(matin)[1]),'d')
    temprow=copy.deepcopy(matin[r1,:])
#    temprow=matin[r1,:]
    matin[r1,:]=matin[r2,:]
    matin[r2,:]=temprow
    return matin

def minindex(listin):
    mymin=min(listin)
    for x, ent in enumerate(listin):
        if ent==mymin:
            return x

def maxindex(listin):
    mymax=max(listin)
    for x, ent in enumerate(listin):
        if ent==mymax:
            return x

def ToLatexString(strin,appenddol=1):
    outstr=strin.lower()
    latexlist=['theta','alpha','beta','gamma','delta']
    ind=outstr.find('_')
    if ind>-1:
        checkstr=outstr[0:ind]
        if checkstr in latexlist:
            outstr='\\'+outstr
    if appenddol:
        outstr='$'+outstr+'$'
    return outstr

def isfloat(objin):
    return isinstance(objin,float)

def SymstrMattoMaxima(matin, symname):
    matstr=''
    for currow in matin.tolist():
        tempstr=str(currow)
        rowstr=tempstr.replace("'","")
        if matstr:
            matstr+=','
        matstr+=rowstr
    return symname+':matrix('+matstr+')'


def rflat(seq2):
    seq = []
    for entry in seq2:
	if seqin([entry]):
            seq.extend([i for i in entry])
        else:
            seq.append(entry)
    return seq

def seqin(sequence):
    for i in sequence:
	#if ('__contains__' in dir(i) and    ## all sequences have '__contains__' in their dir()
         #         type(i) != str and type(i) != dict and type(i) != symstr): ## parentheses present to aid commenting mid-condition
         if type(i)==list or type(i)==tuple:
            return True
    return False

def flatten(seq):
#    Pdb().set_trace()
    while seqin(seq):
        seq = rflat(seq)
    return seq

def find_unique(listin):
    temp = [1]*len(listin)
    mydict = dict(zip(listin, temp))
    return mydict.keys()
