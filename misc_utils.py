from numpy import column_stack, savetxt

import os

lf = os.linesep#determing the linefeed for the operating system ('\n' for Linux or '\r\n' for Windows)

def _dump_matrix(f, matrix, fmt='%0.10g', delim='\t'):
    savetxt(f, matrix, fmt=fmt, delimiter=delim)
    return f
    
def _dump_vectors(f, vectorlist, fmt='%0.10g', delim='\t'):
    mymatrix = column_stack(vectorlist)#create a matrix with each vector as a column
    _dump_matrix(f, mymatrix, fmt=fmt, delim=delim)


def _open_file(filename):
    f = open(filename, 'w')#open a file for writing.  Caution: this will overwrite an existing file
    return f


def _save_labels(f, labels, delim='\t'):
    firstrow = delim.join(labels)#create a delimited first row of the labels
    f.write(firstrow+'\n')#write the first row and a line feed to the file
    return f
    
def dump_vectors(filename, vectorlist, labels, fmt='%0.10g', delim='\t'):
    """Dump a list of vectors to a text file where each vector is a
    columnm in a spreadsheet style text file.

    filename is a string containing the filename or path to the file
    to be saved.  It will be overwritten if it exists.

    labels is a list of strings containing the labels for the columns
    in the file.

    fmt is the format for converting numbers to strings when creating
    the text file.

    delim is the delimiter to use between columns of the file.  The
    default is a tab."""
    f = _open_file(filename)
    _save_labels(f, labels, delim=delim)
    _dump_vectors(f, vectorlist, fmt=fmt, delim=delim)
    f.close()#close the file

    
def dump_matrix(filename, matrix, labels, fmt='%0.10g', delim='\t'):
    """Similar to dump_vectors, but the data is already a matrix that
    needs to be dumped to a file with a lable row."""
    f = _open_file(filename)
    _save_labels(f, labels, delim=delim)
    _dump_matrix(f, matrix, fmt=fmt, delim=delim)
    f.close()#close the file


