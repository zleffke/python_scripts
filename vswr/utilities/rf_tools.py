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

def cap_impedance(C, f):
    '''
    Compute complex impedance of capacitor
    C: capacitance [farads]
    f: frequency [hertz]
    '''
    x_c = np.cdouble(real=0, imag=(2*np.pi*f*c)^-1)

def reflection_coefficient(z_l,z_0):
    '''
    Compute VSWR from complex impedance
    z_l: load impedance
    z_0: source or reference impedance
    '''
    Gamma = (z_l - z_0)/(z_l + z_0)
    return Gamma

def vswr_impedance(z_l, z_0):
    '''
    Compute VSWR from complex impedance
    z_l: load impedance
    z_0: source or reference impedance
    '''
    ref_co = reflection_coefficient(z_l,z_0)
    ref_co_mag = abs(ref_co)
    vswr = (1+abs(ref_co))/(1-abs(ref_co))
    return vswr