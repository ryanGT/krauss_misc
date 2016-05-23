import txt_mixin

def readfile_to_list(pathin, strip=True):
    """Read file into a list of lines.  Strip off newline symbols if
    strip=True"""
    f=open(pathin,'r')
    listin=f.readlines()
    f.close()

    if strip:
        listout = [line.strip() for line in listin]
    else:
        listout = listin
        
    return listout


def add_newlines(listin):
    listout = []
    for line in listin:
        if not line:
            # if line is blank or empty, replace it
            # with a newline character
            listout.append('\n')
        elif line[-1]!='\n':
            # if last character is not a newline, append one
            # note, this might not be great if the last character
            # was a carriage return
            listout.append(line+'\n')
        else:
            # if the last character was a newline, do nothing
            listout.append(line)
    return listout


def writefile(pathin, listin, append=False):
    if append and os.path.exists(pathin):
        openstr = 'ab'
    else:
        openstr = 'wb'
    f = open(pathin, openstr)
    listout = add_newlines(listin)
    f.writelines(listout)
    f.close()


def combined_spreadsheets(pathlist):
    """Combined a list of spreadsheets where the first row is assumed
    to contain the labels.  Output one big spreadsheet with the same
    labels."""

    first = True

    combined_list = []

    for curpath in pathlist:
        curlist = readfile_to_list(curpath)
        curlabels = curlist.pop(0)# grab first line and remove it from the list

        if first:
            labels = curlabels
            combined_list.append(labels)
            first = 0
        else:
            # check that labels are the same
            assert curlabels == labels, "problem with mismatched labels"

        combined_list.extend(curlist)# labels have been removed by pop command

    return combined_list
    
