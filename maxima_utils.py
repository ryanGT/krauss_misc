def row_to_maxima_line(rowin, fmt='%0.9g'):
    str_list = [fmt % item for item in rowin]
    row_str = '[' + ','.join(str_list) +']'
    return row_str


def matrix_to_maxima_lines(matin, lhs):
    #U0:matrix([1,0,0,0,0],[0,1,1.0/((c_spring*s + k_spring)*(Gth*H*K_act*m1/(s*(p_act1 + s)) + 1.0)),0,Gth*K_act*m1/(s*(p_act1 + s)*(Gth*H*K_act*m1/(s*(p_act1 + s)) + 1.0))],[0,0,1,0,0],[0,0,0,1,0],[0,0,0,0,1])$
    str_out = lhs + ':matrix('

    for row in matin:
        str_out += row_to_maxima_line(row)
        str_out += ','

    if str_out[-1] == ',':
        str_out = str_out[0:-1]

    str_out += ')$'
    return str_out
    
    
            
