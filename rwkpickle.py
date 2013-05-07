import cPickle

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
