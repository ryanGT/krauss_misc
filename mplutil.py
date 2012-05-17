"""Miscelaneous functions I wrote for conveince in using matplotlib
(translated from rwkmplutil to be compatible with wxmpl and embedding
in WX apps - should be compatible with all OO interface usages).

This file should replace oomplutil.  As I move away from pylab to OO usage,
it should also replace rwkmplutil."""
from __future__ import division
import matplotlib, os
from numpy import column_stack

from IPython.core.debugger import Pdb


def subplot212(fig, x, y1, y2, xlabel='Time (sec)', y1label=None, y2label=None, legend1=[], legend2=[]):
    a1 = fig.add_subplot(2, 1, 1)
    a1.plot(x, y1)
    a1.grid(True)
    if y1label:
        a1.set_ylabel(y1label)
    if legend1:
        a1.legend(legend1)
    for ticklabel in a1.get_xticklabels():
        ticklabel.set_visible(False)

    a2 = fig.add_subplot(2, 1, 2, sharex=a1)
    a2.plot(x, y2)
    a2.grid(True)
    a2.set_xlabel('Time (sec)')
    if y2label:
        a2.set_ylabel(y2label)
    if legend2:
        a2.legend(legend2)


def GridsOn(fig):
    for ax in fig.axes:
        ax.grid(True)


def SetAllXlims(fig, xlim):
    """Set the xlims for all axes of fig to the list xlim."""
    for axis in fig.axes:
        axis.set_xlim(xlim)

def SetXlim(fig, xlim):
    """alias for SetAllXlims"""
    return SetAllXlims(fig, xlim)


def SetYlim(fig, ylim, axis=0):
    """alias for SetAllXlims"""
    fig.axes[axis].set_ylim(ylim)


def GetMagAxis(fig, axis=None):
    if axis is None:
        if len(fig.axes) == 2:
            axis = 0
        elif len(fig.axes) == 3:
            axis = 1
        else:
            axis = 0
    return axis

def SetMagLim(fig, maglim, axis=None):
    """Set the magnitude limits of a Bode plot by calling SetYLim
    attempting to intelligently determine the phase axis if axis is
    None.  If fig has two axes, this is assumed to be a Bode plot
    without coherence and axis=0.  If fig has 3 axes, this is assumed
    to be a Bode+Coherence plot with magnitude on axis 1.  Axis can be
    mannually overridden if necessary."""
    axis = GetMagAxis(fig, axis)
    SetYLim(fig, maglim, axis)


def SetMagTicks(fig, ticks, axis=None):
    """Set the magnitude yticks of a Bode plot by calling SetYLim
    attempting to intelligently determine the phase axis if axis is
    None.  If fig has two axes, this is assumed to be a Bode plot
    without coherence and axis=0.  If fig has 3 axes, this is assumed
    to be a Bode+Coherence plot with magnitude on axis 1.  Axis can be
    mannually overridden if necessary."""
    axis = GetMagAxis(fig, axis)
    SetYTicks(fig, ticks, axis)


def GetPhaseAxis(fig, axis=None):
    if axis is None:
        if len(fig.axes) == 2:
            axis = 1
        elif len(fig.axes) == 3:
            axis = 2
        else:
            axis = -1
    #if axis is not None, this will just pass back what was passed in
    return axis


def SetPhaseLim(fig, phaselim, axis=None):
    """Set the phase limits of a Bode plot by calling SetYLim,
    attempting to intelligently determine the phase axis if axis is
    None.  If fig has two axes, this is assumed to be a Bode plot
    without coherence and axis=1.  If fig has 3 axes, this is assumed
    to be a Bode+Coherence plot with phase on axis 2.  Axis can be
    mannually overridden if necessary."""
    axis = GetPhaseAxis(fig, axis)
    SetYLim(fig, phaselim, axis)

def SetPhaseTicks(fig, ticks, axis=None):
    """Set the phase yticks of a Bode plot by calling SetYTicks,
    attempting to intelligently determine the phase axis if axis is
    None.  If fig has two axes, this is assumed to be a Bode plot
    without coherence and axis=1.  If fig has 3 axes, this is assumed
    to be a Bode+Coherence plot with phase on axis 2.  Axis can be
    mannually overridden if necessary."""
    axis = GetPhaseAxis(fig, axis)
    SetYTicks(fig, ticks, axis)


def SetCohLim(fig, cohlim, axis=0):
    """Set the coherence limits of a Bode plot by calling SetYLim
    assuming the coherence is plotted on axis 2). Axis can be
    overridden if necessary."""
    SetYLim(fig, cohlim, axis)


def SetYLim(fig, ylim, axis=0):
    """Set the ylim of fig.axes[axis] to ylim."""
    fig.axes[axis].set_ylim(ylim)


def SetYTicks(fig, ticks, axis=0):
    fig.axes[axis].set_yticks(ticks)


def SetTitle(fig, title, axis=0):
    fig.axes[axis].set_title(title)


def Increase_YLim(ax, ypos, yneg=None):
    if yneg is None:
        yneg = ypos
    else:
        yneg = abs(yneg)
    y1, y2 = ax.get_ylim()
    ax.set_ylim([y1-yneg, y2+ypos])


def Legend(legend_list, fig, axis=0, loc=3):
    fig.axes[axis].legend(legend_list, loc)


def SetLegend(fig, legend_list=None, axis=0, loc=3):
    #print('axis=%s' % axis)
    if type(axis) == str:
        axis = int(axis)
    if axis == 211:
        axis = 0
    elif axis == 212:
        axis = 1
    elif axis == 311:
        axis = 0
    elif axis == 312:
        axis = 1
    elif axis == 313:
        axis = 2
    #print('axis=%s' % axis)
    if legend_list is not None:
        fig.axes[axis].legend(legend_list, loc)
    else:
        fig.axes[axis].legend(loc=loc)


def create_numbered_subscripts(labelin, nc):
    if nc == 1:
        #just make a list out of it
        return [labelin]
    else:
        usetex = bool(labelin[-1] == '$')
        if usetex:
            baselabel = labelin[0:-1]
        else:
            baselabel = labelin
        baselabel += '_{%i}'
        if usetex:
            baselabel += '$'
        for i in range(nc):
            curlabel = baselabel % (i+1)
            if i == 0:
                labelsout = [curlabel]
            else:
                labelsout.append(curlabel)
        return labelsout


def plot_cols(ax, t, mat, clear=True, leg=None, ylabel=None, \
              xlabel='Time (sec)', legloc=1, ylim=[], xlim=[], \
              linetypes=None, labels=None, **kwargs):
    if clear:
        ax.clear()
    if linetypes is None:
        nr, nc = mat.shape
        linetypes = ['-']*nc
    nr, nc = mat.shape
    if labels is None:
        labels = [None]*nc
    elif type(labels) == str:
        #create labels with numbered subscripts if needed
        labels = create_numbered_subscripts(labels, nc)
    for col, lt, label in zip(mat.T, linetypes, labels):
        ax.plot(t, col, lt, label=label, **kwargs)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if leg:
        #print('leg=%s' % leg)
        #print('legloc=%s' % legloc)
        ax.legend(leg, loc=legloc)
    if ylim:
        ax.set_ylim(ylim)
    if xlim:
        ax.set_xlim(xlim)


def plot_vect(ax, t, vect, clear=False, **kwargs):
    """Calls plot_cols with vect made into a matrix of one column.
    See plot_cols for additional options."""
    mat = column_stack([vect])
    plot_cols(ax, t, mat, clear=clear, **kwargs)



def set_Bode_opts(fig, bodeopts, coh=True):
    """set the options of a Bode plot by looking for keys in bodeopts.
       Valid keys include freqlim, maglim, phaselim, and cohlim."""
    mydict={'freqlim':SetAllXlims, 'maglim':SetMagLim, \
            'phaselim':SetPhaseLim}
    if coh:
        mydict.update({'cohlim':SetCohLim})
    defaults={'cohlim':[0,1]}

    for attr, func in mydict.iteritems():
        value = None
        if hasattr(bodeopts, attr):
            value = getattr(bodeopts, attr)
        if not value:
            if defaults.has_key(attr):
                value = defaults[attr]
        if value:
            func(fig, value)




#from pylab import figure, subplot, yticks, xticks, ylabel, xlabel, title, semilogx, gca

## def SetPlotLims(fi,myxlim, ylim1,ylim2=[]):
##     """Set the axis limits of a pylab plot.  If ylim2 is specified,
##     the plot is assumed to be a two level plot and subplot(211) is
##     called before setting its ylim to ylim1 and the subplot(212) is
##     called before setting ylim to ylim2."""
##     pylab.figure(fi)
##     if ylim2:
##         pylab.subplot(211)
##     pylab.xlim(myxlim)
##     pylab.ylim(ylim1)
##     if ylim2:
##         pylab.subplot(212)
##         pylab.xlim(myxlim)
##         pylab.ylim(ylim2)

## def SetXlims(fi,myxlim,subplots):
##     pylab.figure(fi)
##     for sp in subplots:
##         pylab.subplot(sp)
##         pylab.xlim(myxlim)

## def SetXLim(fi,myxlim):
##     """Set the x-axis limits of a pylab plot."""
##     pylab.figure(fi)
##     pylab.xlim(myxlim)

## def SetYLim(fi,myylim,subp=None):
##     pylab.figure(fi)
##     if subp:
##         pylab.subplot(subp)
##     pylab.ylim(myylim)

## def SetCombCoh(fi,myylim):
##     SetYLim(fi,myylim,311)

## def SetCombMag(fi,myylim):
##     SetYLim(fi,myylim,312)

## def SetCombPhase(fi,myylim):
##     SetYLim(fi,myylim,313)

## def SetAllXlims(fig, xlims):
##     """Set the xlim for all axess on a figure."""
##     for curax in fig.axes:
##         curax.set_xlim(xlims)

## def _SetYLim(fig, ylims, rowNum):
##     """Set the ylim of the subplot whose ax.rowNum==rowNum."""
##     if ylims:
##         for curax in fig.axes:
##             if curax.rowNum == rowNum:
##                 curax.set_ylim(ylims)
##                 break


## def SetMagLim(fig, maglim, rowNum=0):
##     """Set the magnitude limits of a Bode plot, assuming the magnitude
##     portion is in row 0 of the plot (i.e. the top row of
##     subplots), unless rowNum is specified."""
##     _SetYLim(fig, maglim, rowNum)

## def SetPhaseLim(fig, phaselim, rowNum=1):
##     """Set the phase limits of a Bode plot, assuming the phase
##     portion is in row 1 of the plot (i.e. the second row of
##     subplots), unless rowNum is specified."""
##     _SetYLim(fig, phaselim, rowNum)


def mysave(path_in, fig, ext='.eps', dpi=100):
    if isinstance(fig, matplotlib.axes.Axes):
        fig = fig.figure#you really sent me an axis
    if ext[0] != '.':
        ext = '.'+ext
    path_no_ext, ext_in = os.path.splitext(path_in)
    if ext_in:
        ext = ext_in
    kwargs = {}
    if ext == '.pdf':
        ext = '.eps'
    elif ext == '.png':
        kwargs['dpi'] = dpi
    path_out = path_no_ext + ext
    fig.savefig(path_out, **kwargs)
    if ext == '.eps':
        cmd = 'epstopdf %s' % path_out
        print('cmd='+cmd)
        os.system(cmd)


## def MagLegend(fi,legend,legloc):
##     """Place the legend of fi on the magnitude portion of Bode plot by
##     calling SetLegend(fi,legend,legloc,211)."""
##     SetLegend(fi,legend,legloc,211)

## def PhaseLegend(fi,legend,legloc):
##     """Place the legend of fi on the phase portion of Bode plot by
##     calling SetLegend(fi,legend,legloc,212)."""
##     SetLegend(fi,legend,legloc,212)

## def SetLegend(fi,legend,legloc,subplotnum=None):
##     """Set the legend of figure fi at location legloc.  If subplotnum
##     is specified, call subplot(subplotnum) before calling legend.

##     legloc follows standard pylab notation:
##     1-Upper Right
##     2-Upper Left
##     3-Lower Left
##     4-Lower Right"""
##     pylab.figure(fi)
##     if subplotnum:
##         pylab.subplot(subplotnum)
##     pylab.legend(legend,legloc)

## def _SetTicks(fi,vector,subp=None):
##     pylab.figure(fi)
##     if subp:
##         pylab.subplot(subp)
##     pylab.yticks(vector)

## def SetCombPhaseTicks(fi,vector):
##     _SetTicks(fi,vector,subp=313)

## def SetCombMagTicks(fi,vector):
##     _SetTicks(fi,vector,subp=312)

## def SetCombCohTicks(fi,vector):
##     _SetTicks(fi,vector,subp=311)

## def SetMagTicks(fi,vector,subp=211):
##     """Set the magnitude tick marks by calling pylab.yticks on
##     subplot(211)."""
##     pylab.figure(fi)
##     pylab.subplot(subp)
##     pylab.yticks(vector)

## def SetPhaseTicks(fi,vector,subp=212):
##     """Set the phase tick marks by calling pylab.yticks on
##     subplot(212)."""
##     pylab.figure(fi)
##     pylab.subplot(subp)
##     pylab.yticks(vector)

## def myhline(y,linetype,linewidth=0.4,xlim=None):
##     if xlim is None:
##         myxlim=pylab.xlim()
##     else:
##         myxlim=xlim
##     mylines=pylab.plot(myxlim,[y,y],linetype,linewidth=linewidth)
##     myline=mylines[0]
##     myline.set_zorder(-20)

## def myvline(x,linetype,linewidth=0.4,ylim=None,mysub=None):
##     if mysub:
##         subplot(mysub)
##     if ylim is None:
##         myylim=pylab.ylim()
##     else:
##         myylim=ylim
##     mylines=pylab.plot([x,x],myylim,linetype,linewidth=linewidth)
##     myline=mylines[0]
##     myline.set_zorder(-20)

## def vlinelist(fi, x, sublist=[211,212],linetype='k--', linewidth=0.4, ylim=None):
##     figure(fi)
##     for sub in sublist:
##         if type(x)==float or type(x)==int:
##             mylist=[x]
##         else:
##             mylist=x
##             for curx in mylist:
##                 myvline(curx, linetype, linewidth, mysub=sub)

## def DropBottomYtick(fi, subp=None):
##     figure(fi)
##     if subp:
##         subplot(subp)
##     curticks=yticks()
##     oldticks=curticks[0]
##     newticks=oldticks[1:]
##     yticks(newticks)

## def DropBottomYticks(fi, subplist):
##     for item in subplist:
##         DropBottomYtick(fi, subp=item)

## #from rwkbode import MyFormatter

## from matplotlib.ticker import LogFormatterMathtext

## class MyFormatter(LogFormatterMathtext):
##    def __call__(self, x, pos=None):
##        if pos==0: return ''  # pos=0 is the first tick
##        else: return LogFormatterMathtext.__call__(self, x, pos)

## def SetLogXFormatter(fi, mysubplot=None):
##     figure(fi)
##     if mysubplot:
##         subplot(mysubplot)
##     ax=gca()
##     ax.xaxis.set_major_formatter(MyFormatter())

## def SetAllLogXFormatters(fi, subplist):
##     for cursubp in subplist:
##         SetLogXFormatter(fi,cursubp)

## def SetBothLogXFormatters(fi):
##     SetAllLogXFormatters(fi,[211,212])
