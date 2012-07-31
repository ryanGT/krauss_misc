from scipy import *
import sympy
import copy, re
#from IPython.core.debugger import Pdb
import pdb

def expr_to_Maxima_string(expr):
    """Take a symbolic sympy expression expr and convert it to a
    Maxima compatilbe string that will be saved to a batch file.  I
    can't find a sympy printer that already does this."""
    string = str(expr)
    string = string.replace('**','^')
    #replace imaginary number I
    p = re.compile('\\bI\\b')
    string = p.sub('%i',string)
    return string


def matrix_to_Maxima_string(matin, matname):
    outstr = matname + ':matrix('
    nr, nc = matin.shape
    for i in range(nr):
        rowstr = '['
        for j in range(nc):
            elemstr = expr_to_Maxima_string(matin[i,j])
            rowstr += elemstr
            if j < (nc-1):
                rowstr += ','
        rowstr += ']'
        outstr += rowstr
        if i < (nr-1):
            outstr += ','
##     Ubeamz:matrix([c1bz,1/2*Lbz*c4bz/betabz,-1/2*abz*c3bz/betabz^2,-1/2*Lbz*abz*c2bz/betabz^3],[1/2*betabz*c2bz/Lbz,c1bz,1/2*abz*c4bz/betabz/Lbz,1/2*abz*c3bz/betabz^2],[-1/2*betabz^2*c3bz/abz,1/2*betabz*Lbz*c2bz/abz,c1bz,-1/2*Lbz*c4bz/betabz],[-1/2*betabz^3*c4bz/Lbz/abz,1/2*betabz^2*c3bz/abz,-1/2*betabz*c2bz/Lbz,c1bz])$
    outstr += ')$'
    return outstr

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
    mydefaults = {"mode": 'plain', \
                  #"inline" : None,
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


def matrix_subs(M, sub_dict):
    temp = copy.copy(M)
    out_list = temp.tolist()
    for r, row in enumerate(out_list):
        for i, item in enumerate(row):
            item_out = item.subs(sub_dict)
            row[i] = item_out
        out_list[r] = row
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


class equation(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return self.lhs.__repr__() + ' = ' + self.rhs.__repr__()

    def __add__(self, other):
        new_eq = equation(self.lhs+other, self.rhs+other)
        return new_eq

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        new_eq = equation(self.lhs*other, self.rhs*other)
        return new_eq

    def expand(self):
        new_lhs = sympy.expand(self.lhs)
        new_rhs = sympy.expand(self.rhs)
        new_eq = equation(new_lhs, new_rhs)
        return new_eq

    def ToLatex(self, *args, **kwargs):
        profile = {'mode':'plain'}
        lhsstr = sympy.latex(self.lhs, profile)
        rhsstr = sympy.latex(self.rhs, profile)
        return lhsstr + ' = ' + rhsstr
