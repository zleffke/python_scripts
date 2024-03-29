#! /usr/bin/python3

"""
RF functions for calculating stuff (VSWR, S11, etc.)
"""

import sys
import os
import math
import string
import struct
import numpy as np
import scipy
import datetime as dt
import pytz
import pandas as pd

def xc_to_capacitance(Xc,f):
    return 1/(2*np.pi*f*-1*np.imag(Xc))

def x2l_to_inductance(X_2L, f):
    return np.imag(X_2L)/(4*np.pi*f)

def tee_tuner_vec(X, X_2L, Z_load):
    '''
    X[0] = X_c1
    X[1] = X_c2
    '''
    print(X[0])
    X_p1 = 1/((1)/(X_2L) + (1)/(X[1]+Z_load))
    X_p2 = X[0] + 1/((1)/(X_2L)+(1)/(X_p1))
    return X_p2

def tee_tuner(X_c1,X_c2,X_2L, Z_ant):
    X_p1 = 1/((1)/(X_2L) + (1)/(X_c2+Z_ant))
    X_p2 = X_c1 + 1/((1)/(X_2L)+(1)/(X_p1))
    return X_p2

def capacitor_impedance(C, f):
    '''
    Compute complex impedance of capacitor
    C: capacitance [farads]
    f: frequency [hertz]
    '''
    return complex(real=0, imag=-1/(2*np.pi*f*C))

def inductor_impedance(L, f):
    '''
    Compute complex impedance of capacitor
    L: inductance [henries]
    f: frequency [hertz]
    '''
    return complex(real=0, imag=2*np.pi*f*L)

def reflection_coefficient(z_l,z_0):
    '''
    Compute VSWR from complex impedance
    z_l: load impedance
    z_0: source or reference impedance
    '''
    Gamma = (z_l - z_0)/(z_l + z_0)
    rho = abs(Gamma)
    return rho,Gamma

def vswr_impedance(z_l, z_0):
    '''
    Compute VSWR from complex impedance
    z_l: load impedance
    z_0: source or reference impedance
    '''
    rho,Gamma = reflection_coefficient(z_l,z_0)
    vswr = (1+rho)/(1-rho)
    return vswr, Gamma, rho

def return_loss_rho(rho):
    '''
    Compute Return Loss from refl coefficient magnitude
    rho: magnitude of reflection coefficient
    '''
    RL=20*np.log10(rho)
    rl = np.power(10,RL/10)
    return rl, RL

def return_loss_vswr(vswr):
    '''
    Compute Return Loss from VSWR
    vswr: voltage standing wave ratio
    '''
    RL=20*np.log10((vswr-1)/(vswr+1))
    rl = np.power(10,RL/10)
    return rl, RL

def power_reflected(rl,P):
    '''
    Compute power reflected 
    rl: return loss, linear scale
    P: Forward Power, watts
    '''
    p = rl*P
    return p

def print_tuner_tee_schematic():
    '''
    ASCII Art print of 'tee' tuner schematic
    '''
    sch = ""
    sch += "         ------              ------           \n"
    sch += "  -------| C1 |--------------| C2 |-------    \n"
    sch += "  |      ------      |       ------      |    \n"
    sch += "-----     XCVR     -----      ANT      -----  \n"
    sch += "|   |              |   |               |   |  \n"
    sch += "| Xs|XCVR          | L |IND            | Xl|ANTENNA\n"
    sch += "|   |              |   |               |   |  \n"
    sch += "-----              -----               -----  \n"
    sch += "  |                  |                   |    \n"
    sch += " GND                GND                 GND   \n"
    print(sch)