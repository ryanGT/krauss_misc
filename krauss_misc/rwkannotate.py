import matplotlib.pyplot as plt
import numpy as np


def horiz_dim(ax, x_left, x_right, mylabel, \
              y_start_left=0, y_start_right=None,\
              height_frac=0.1, \
              arrow_len_frac=0.1, \
              head_width_frac=0.03, head_len_frac=0.15, \
              x_label_offset_frac=0, y_label_offset_frac=0, \
              y_line_offset_frac=0.05, y_dim_shift_frac=0.2, \
              arrow_dir=1):
    """Create a dimension between two x points, x_left, 
    x_right.  The dimension bar will have a height of 
    height_frac*(y_max-y_min). """
    y_min, y_max = ax.get_ylim()
    y_span = y_max-y_min
    x_min, x_max = ax.get_xlim()
    x_span = x_max-x_min

    height = height_frac*y_span
    arrow_len = arrow_len_frac*x_span
    head_length = arrow_len*head_len_frac
    head_width = head_width_frac*y_span

    x_label_offset = x_label_offset_frac*x_span
    print("x_label_offset: %s" % x_label_offset)
    y_label_offset = y_label_offset_frac*y_span
    y_line_offset = y_line_offset_frac*height
    y_dim_shift = y_dim_shift_frac*height

    x1 = x_left
    x2 = x_right
    if y_start_right is None:
        y_start_right = y_start_left

    kwargs = {"length_includes_head":1, "fc":'k', "ec":'k', \
              "head_width":head_width, "head_length":head_length}
    line_top = height+y_start_left
    dim_height = line_top - y_dim_shift
    if arrow_dir == 1:
        ax.arrow(x1+arrow_len, dim_height, -arrow_len, 0, **kwargs)
        ax.arrow(x2-arrow_len, dim_height, arrow_len, 0, **kwargs)
    else:
        ax.arrow(x1-arrow_len, dim_height, arrow_len, 0, **kwargs)
        ax.arrow(x2+arrow_len, dim_height, -arrow_len, 0, **kwargs)
    

    x_text = (x1+x2)/2+x_label_offset
    print("line_top = %s" % line_top)
    y_bottom_left = y_start_left+y_line_offset
    print("y_bottom_left = %s" % y_bottom_left)
    print("x_text = %s" % x_text)
    print("x1 = %s" % x1)
    ax.text((x1+x2)/2+x_label_offset, dim_height+y_label_offset, mylabel)
    ax.plot([x1,x1],[y_bottom_left, \
                     line_top], \
            'k', label=None)
    ax.plot([x2,x2],[y_start_right+y_line_offset, \
                     line_top], \
            'k', label=None)



def label_point(ax, x, y, mylabel, x_offset=10, y_offset=10, fmt='ro'):
    ax.plot([x], [y],fmt)
    ax.annotate(mylabel,
                xy=(x, y), xycoords='data',
                xytext=(x_offset, y_offset), textcoords='offset points',
                arrowprops=dict(facecolor='black', arrowstyle="->"),
                horizontalalignment='center', verticalalignment='bottom')


def get_search_indices(t, t_search, p_search=0.1):
    tspan = t.max()-t.min()
    t_min = t_search - p_search*tspan
    t_max = t_search + p_search*tspan
 
    ind_start = np.where(t>t_min)[0][0]
    ind_end = np.where(t>t_max)[0][0]
    return ind_start, ind_end



def find_peak_ind(t, y, t_search, p_search=0.1):
    """Search for a peak in signal y near t_search.  Search within the 
    range +/- p_seach*(t.max()-t.min())

    t is a 1d array for time and y is a 1d signal array, both should
    have the same length.

    returns index, t[index], y[index]

    where index is the index of the peak found"""
    ind_start, ind_end = get_search_indices(t, t_search, p_search)
    y_search = y[ind_start:ind_end]
    ind_a = np.argmax(y_search)
    ind_out = ind_a + ind_start

    return ind_out, t[ind_out], y[ind_out]


def find_zero_crossing(t, y, t_search, p_search=0.1):
    ind_start, ind_end = get_search_indices(t, t_search, p_search)
    #print(ind_start, ind_end)
    y_search = y[ind_start:ind_end]
    y_shift = y_search[1:]
    product = y_search[0:-1]*y_shift
    ind = np.where(product <= 0)
    if len(ind) > 0:
        ind_out = ind[0][0] + ind_start
        return ind_out, t[ind_out], y[ind_out]
    else:
        return None

