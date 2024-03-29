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

def capacitor_impedance(C, f):
    '''
    Compute complex impedance of capacitor
    C: capacitance [farads]
    f: frequency [hertz]
    '''
    imag = -1/(2*np.pi*f*C)
    X_c = complex(real=0, imag=imag)
    return X_c

def inductor_impedance(L, f):
    '''
    Compute complex impedance of capacitor
    L: inductance [henries]
    f: frequency [hertz]
    '''
    X_l = complex(real=0, imag=2*np.pi*f*L)
    return X_l

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