from scipy import *
import sympy
import copy
from IPython.Debugger import Pdb


def find_highest_power(nested_list):
    hp = 0
    for coeff, power in nested_list:
        if int(power) > hp:
            hp = int(power)
    return hp


def str_to_poly(strin):
    """Convert a string to a scipy polynomial."""
    P = sympy.Polynomial(strin)
    coeff_tuple = P.coeffs
    hp = find_highest_power(coeff_tuple)
    coeffs = zeros((hp+1,))

    for coeff, power in coeff_tuple:
        coeffs[hp-int(power)] = float(coeff)
    return poly1d(coeffs)


def mat_to_str(M, profile=None, **kwargs):
    mydefaults = {"inline" : None,
                  "mat_str" : "bmatrix",
                  "mat_delim" : None,
                  "descending" : True,
                  "mainvar" : 's',
                  }
    if profile is not None:
        mydefaults.update(profile)
    profile = mydefaults
    profile.update(kwargs)
    str_out = sympy.latex(M, profile=profile)
    str_out = str_out.replace('\\frac', '\\displaystyle \\frac')
    return str_out


def collect_multiple(variable, collect_list):
    var_out = variable
    for cur_symbol in collect_list:
        var_out = sympy.collect(var_out, cur_symbol)
    return var_out
    

def simplify_coeffs(variable, variable_list):
    rest = copy.copy(variable)
    first = 1
    for cur_var in variable_list:
        cur_coeff = rest.coeff(cur_var)
        rest = sympy.expand(rest - cur_coeff*cur_var)
        if first:
            out = cur_var*sympy.simplify(cur_coeff)
            first = 0
        else:
            out += cur_var*sympy.simplify(cur_coeff)
    out += rest
    return out

    
def list_collect_v1(row, listin):
    rowout = copy.copy(row)
    for c, item in enumerate(rowout):
        temp = item
        for var in listin:
            temp = sympy.collect(temp, var)
        rowout[c] = temp
    return rowout


def list_func(listin, func, *args, **kwargs):
    listout = copy.copy(listin)
    for c, item in enumerate(listout):
        temp = func(item, *args, **kwargs)
        listout[c] = temp
    return listout


def list_collect(row, listin):
    return list_func(row, collect_multiple, listin)


def list_simplify(row):
    return list_func(row, sympy.simplify)


def matrix_func(M, func, *args, **kwargs):
    temp = copy.copy(M)
    out_list = temp.tolist()
    for r, row in enumerate(out_list):
        row_out = list_func(row, func, *args, **kwargs)
        out_list[r] = row_out
    outmat = sympy.Matrix(out_list)
    return outmat
        
    
def matrix_collect_v1(M, listin):
    temp = copy.copy(M)
    out_list = temp.tolist()
    
    for r, row in enumerate(out_list):
        row_out = list_collect(row, listin)
        out_list[r] = row_out
    outmat = sympy.Matrix(out_list)
    return outmat


def matrix_expand(M):
    return matrix_func(M, sympy.expand)


def matrix_simplify(M):
    return matrix_func(M, sympy.simplify)


def matrix_collect(M, listin):
    return matrix_func(M, collect_multiple, listin)

    
def declare_many_sims(listin, namespace=globals()):
    for sym in listin:
        cmd = '%s = sympy.Symbol("%s")' % (sym, sym)
        exec(cmd, namespace)


def diag(i, j):
    if i == j:
        return 1
    else:
        return 0


def eye(N):
    return sympy.Matrix(N, N, diag)
