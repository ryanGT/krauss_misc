import control
from control import TransferFunction as TF

def sotf(z,wn):
    G = TF(wn**2,[1,2*z*wn,wn**2])
    return G
