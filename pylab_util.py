import mplutil
reload(mplutil)

import pylab as PL

import os

from IPython.Debugger import Pdb


def _get_fig(fi=None):
    if fi is not None:
        myfig = PL.figure(fi)
    else:
        myfig = PL.gcf()
    return myfig


def _get_first_axis(fi=None):
    myfig = _get_fig(fi)
    return myfig.get_axes()[0]


def mysave(path_in, fi=None, ext='.eps', dpi=100):
    myfig = _get_fig(fi)
    mplutil.mysave(path_in, myfig, ext=ext, dpi=dpi)


def plot_cols(t, mat, fi=1, clear=True, leg=None, ylabel=None, \
              xlabel='Time (sec)', legloc=1, ylim=[], xlim=[], \
              **kwargs):
    PL.figure(fi)
    if clear:
        PL.clf()
    for col in mat.T:
        PL.plot(t, col, **kwargs)
    if ylabel:
        PL.ylabel(ylabel)
    if xlabel:
        PL.xlabel(xlabel)
    if leg:
        PL.legend(leg, loc=legloc)
    if ylim:
        PL.ylim(ylim)
    if xlim:
        PL.xlim(xlim)

        
def Increase_YLim(ypos, yneg=None, fi=None):
    ax = _get_first_axis(fi)
    mplutil.Increase_YLim(ax, ypos, yneg)

    
def my_plot(x, y, fi=1, clear=True, leg=None, ylabel=None, \
              xlabel='Time (sec)', legloc=1, ylim=[], xlim=[], \
              **kwargs):
    PL.figure(fi)
    if clear:
        PL.clf()
    PL.plot(x, y, **kwargs)
    if ylabel:
        PL.ylabel(ylabel)
    if xlabel:
        PL.xlabel(xlabel)
    if leg:
        PL.legend(leg, loc=legloc)
    if ylim:
        PL.ylim(ylim)
    if xlim:
        PL.xlim(xlim)
    

def SetTitle(fignum, title, axis=0):
    fig = PL.figure(fignum)
    mplutil.SetTitle(fig, title, axis=axis)
    

def SetAllXlims(fi, xlim):
    fig = _get_fig(fi)
    mplutil.SetAllXlims(fig, xlim)
    

## def SetMagLim(fi, maglim, axis=None):
##     fig = _get_fig(fi)
##     mplutil.SetMagLim(fig, maglim, axis)


def _call_mplutil_w_fig(fi, funcname, *arg, **kwargs):
    fig = _get_fig(fi)
    func = getattr(mplutil, funcname)
    return func(fig, *arg, **kwargs)


def SetMagLim(fi, *args, **kwargs):
    return _call_mplutil_w_fig(fi, 'SetMagLim', *args, **kwargs)


def SetPhaseLim(fi, *args, **kwargs):
    return _call_mplutil_w_fig(fi, 'SetPhaseLim', *args, **kwargs)


def SetLegend(fi, *args, **kwargs):
    return _call_mplutil_w_fig(fi, 'SetLegend', *args, **kwargs)
