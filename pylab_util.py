import mplutil
#reload(mplutil)

import pylab as PL

import os

#from IPython.core.debugger import Pdb


def _get_fig(fi=None):
    if fi is not None:
        myfig = PL.figure(fi)
    else:
        myfig = PL.gcf()
    return myfig


def _get_first_axis(fi=None):
    myfig = _get_fig(fi)
    return myfig.get_axes()[0]


def _get_ext(pathin, ext):
    fno, ext0 = os.path.splitext(pathin)
    if ext0:
        return ext0
    else:
        return ext

def _build_pdf_path(pathin):
    fno, ext0 = os.path.splitext(pathin)
    pdfpath = fno + '.pdf'
    return pdfpath


def mysave(path_in, fi=None, ext='.eps', dpi=100, pdfcrop=1):
    myfig = _get_fig(fi)
    mplutil.mysave(path_in, myfig, ext=ext, dpi=dpi)
    if pdfcrop:
        pdfpath = _build_pdf_path(path_in)
        if os.path.exists(pdfpath):
            cmd = 'pdfcrop %s %s' % (pdfpath, pdfpath)
            print(cmd)
            os.system(cmd)




def plot_cols(t, mat, fi=1, clear=True, leg=None, ylabel=None, \
              xlabel='Time (sec)', legloc=1, ylim=[], xlim=[], \
              figsize=None, \
              **kwargs):
    if figsize is not None:
        PL.figure(fi, figsize)
    else:
        PL.figure(fi)

    if clear:
        PL.clf()
    nr, nc = mat.shape
    if leg is None:
        leg = [None]*nc
    for col, label in zip(mat.T, leg):
        PL.plot(t, col, label=label, **kwargs)
    if ylabel:
        PL.ylabel(ylabel)
    if xlabel:
        PL.xlabel(xlabel)
    if leg:
        PL.legend(loc=legloc)
    if ylim:
        PL.ylim(ylim)
    if xlim:
        PL.xlim(xlim)


def set_ylabel(ylabel, fi=1):
    PL.figure(fi)
    PL.ylabel(ylabel)

def set_xlabel(xlabel, fi=1):
    PL.figure(fi)
    PL.xlabel(xlabel)

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


def SetXTicks(fi, xlim):
    fig = _get_fig(fi)
    mplutil.SetXTicks(fig, xlim)


def SetXlim(fi, xlim):
    fig = _get_fig(fi)
    mplutil.SetXlim(fig, xlim)


def SetYlim(fi, ylim):
    fig = _get_fig(fi)
    mplutil.SetYlim(fig, ylim)


def SetFreqLim(fi, xlim):
    SetAllXlims(fi, xlim)

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


def SetPhaseTicks(fi, *args, **kwargs):
    return _call_mplutil_w_fig(fi, 'SetPhaseTicks', *args, **kwargs)

def SetMagTicks(fi, *args, **kwargs):
    return _call_mplutil_w_fig(fi, 'SetMagTicks', *args, **kwargs)

def set_Bode_opts(fi, bodeopts, coh=True):
    fig = _get_fig(fi)
    mplutil.set_Bode_opts(fig, bodeopts, coh=coh)


def set_custom_dashes(fi, line_id=0, \
                      dash_pattern=[7,4,2,4]):
    fig = _get_fig(fi)
    axes = fig.axes
    mplutil.set_custom_dashes(axes, line_id=line_id, \
                              dash_pattern=dash_pattern)

