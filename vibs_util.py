import pylab as P
from scipy import *


def freq_resp(w, H, \
              xlabel='$\\omega$ (rad./sec.)', \
              maglabel='Mag. Ratio.', \
              phaselabel='Phase (deg.)', \
              fignum=1, clear=True, \
              grid=False, deg=True, dB=False, \
              freqlim=None, **plot_kwargs):
    P.figure(fignum)
    if clear:
        P.clf()
    mag = abs(H)
    if dB:
        mag = 20*log10(mag)
    P.subplot(211)
    P.plot(w, mag, **plot_kwargs)
    P.grid(1)
    P.ylabel(maglabel)
    if freqlim is not None:
        P.xlim(freqlim)
    P.grid(bool(grid))
        
    if deg:
        phase = angle(H,1)
    else:
        phase = angle(H)

    P.subplot(212)
    P.plot(w, phase, **plot_kwargs)
    P.xlabel(xlabel)
    P.ylabel(phaselabel)
    
    if freqlim is not None:
        P.xlim(freqlim)
    P.grid(bool(grid))
