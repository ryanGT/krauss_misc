import wx
import wx.grid

from rwkmisc import reverse

def MoveBetweenListBoxes(sourcebox, destbox):
    indstomove=sourcebox.GetSelections()
#        self.junkfiles
    filestomove=[]
    for ind in reverse(indstomove):
        curstr=sourcebox.GetString(ind)
        filestomove.append(curstr)
        sourcebox.Delete(ind)
    for ent in reverse(filestomove):
        destbox.Append(ent)

def SetListBoxContentsfromString(strin,listbox1,listbox2=None):
    listbox1.Clear()
    if strin=='None':
        return
    listin=strin.split('\t')
    for file in listin:
        listbox1.Append(file)
        if listbox2:
            ind=listbox2.FindString(file)
            if ind!=wx.NOT_FOUND:
                listbox2.Delete(ind)

def SetListBoxContentsfromList(listin,listbox1,listbox2=None):
    listbox1.Clear()
    for file in listin:
        listbox1.Append(str(file))
        if listbox2:
            ind=listbox2.FindString(str(file))
            if ind!=wx.NOT_FOUND:
                listbox2.Delete(ind)

def GetListfromListBox(mylistbox):
    nf=mylistbox.GetCount()
    contents=[]
    for ind in range(nf):
        contents.append(mylistbox.GetString(ind))
    return contents

def GetListBoxContentsasString(mylistbox):
    nf=mylistbox.GetCount()
    strout=''
    first=1
    for ind in range(nf):
        if not first:
            strout+='\t'
        else:
            first=0
        curfile=mylistbox.GetString(ind)
        strout+=curfile
    return strout

def SelectAll(controlwithitems):
    nf=controlwithitems.GetCount()
    for ind in range(nf):
        controlwithitems.SetSelection(ind)

def GetListBoxSelections(mylistbox):
    selected = []
    indices = mylistbox.GetSelections()
    for index in indices:
        curitem = mylistbox.GetString(index)
        selected.append(curitem)
    return selected

def SetListBoxSelections(listofstrings, mylistbox):
    """Set the selections of a listbox based on a list of strings that
    match the items to be selected."""
    for item in listofstrings:
        mylistbox.SetStringSelection(item)

def DeleteFromListbox(controlwithitems, indlist):
    """Remove items from a controlwithitems.  indlist is an list of
    integers of the indices of the items to remove."""
    mylist=list(indlist)
    for index in reverse(mylist):
        controlwithitems.Delete(index)

def SetGridFromSpreadsheet(spreadsheet, mygrid, numrows=200):
    """Display the first numrows rows of spreadsheet, where
    spreadsheet is an instance of my spreadsheet class."""
    mydata = spreadsheet.ReadRows(maxrows=numrows)
    mygrid.ClearGrid()
    ncg = mygrid.GetNumberCols()
    nrg = mygrid.GetNumberRows()
    nrd = len(mydata)
    row1 = mydata[0]
    ncd = len(row1)
    if ncd > ncg:
        mygrid.AppendCols(ncd-ncg)
    if nrd > nrg:
        mygrid.AppendRows(nrd-nrg)
    for r, row in enumerate(mydata):
        for c, item  in enumerate(row):
            mygrid.SetCellValue(r, c, item)

def ClearGridCol(colnum, mygrid):
    nrg = mygrid.GetNumberRows()
    for n in range(nrg):
        mygrid.SetCellValue(n, colnum, '')

def SetGridColFromList(listin, colnum, mygrid):
    nrg = mygrid.GetNumberRows()
    nrd = len(listin)
    if nrd > nrg:
        mygrid.AppendRows(nrd-nrg)
    for r, item in enumerate(listin):
        mygrid.SetCellValue(r, colnum, item)

def AlternateGridRowColor(mygrid, mycolor=None):
    if mycolor is None:
        mycolor = wx.Color(200,200,200)
    attr = wx.grid.GridCellAttr()
    #attr.SetTextColour(wx.BLACK)
    attr.SetBackgroundColour(mycolor)
    #attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
    nrg = mygrid.GetNumberRows()

    for n in range(nrg):
        if n%2:
            mygrid.SetRowAttr(n, attr)

def GetGridColAsList(colnum, mygrid):
    nrg = mygrid.GetNumberRows()
    listout = []
    for r in range(nrg):
        item = mygrid.GetCellValue(r, colnum)
        if item:
            listout.append(item.encode())
    return listout


def GetGridAsNestedList(mygrid):
    nrg = mygrid.GetNumberRows()
    ncg = mygrid.GetNumberCols()
    listout = []
    for r in range(nrg):
        currow = []
        for c in range(ncg):
            item = mygrid.GetCellValue(r, c)
            currow.append(item)
        listout.append(currow)
    return listout

