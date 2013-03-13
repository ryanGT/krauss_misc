from matplotlib.pyplot import *
from scipy import *

def my_annotate(ax, ta, t, y, text, \
                offset=(10,10),
                connectionstyle="angle3,angleA=90,angleB=0"):
    ind = where(t>ta)[0][0]
    x1 = t[ind]
    y1 = y[ind]
    ax.annotate(text,
                xy=(x1, y1), xycoords='data',
                xytext=(x2, y2), textcoords='offset points',
                arrowprops=dict(arrowstyle="->", #linestyle="dashed",
                                color="0.5",
                                shrinkA=5, shrinkB=5,
                                patchA=None,
                                patchB=None,
                                connectionstyle=connectionstyle,
                                ),
                )
    
