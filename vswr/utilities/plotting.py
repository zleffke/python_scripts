#! /usr/bin/python3

"""
Plotting Utilities for Antenna simulations
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

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.dates as mdates
import matplotlib.colors as colors

def plot_pps_fee_subplot(df, o_path = False, idx=0, save=0):
    #---- START Figure 1 ----
    xinch = 14
    yinch = 7
    
    fig1=plt.figure(idx, figsize=(xinch,yinch/.8))
    ax1 = fig1.add_subplot(2,1,1)
    ax2 = fig1.add_subplot(2,1,2)

    #Configure Grids
    ax1.xaxis.set_major_locator(MultipleLocator(10000))
    ax1.xaxis.set_minor_locator(MultipleLocator(2000))
    ax1.xaxis.grid(True,'major', linewidth=1)
    ax1.xaxis.grid(True,'minor', linewidth=0.5)

    ax2.xaxis.set_major_locator(MultipleLocator(10000))
    ax2.xaxis.set_minor_locator(MultipleLocator(2000))
    ax2.xaxis.grid(True,'major', linewidth=1)
    ax2.xaxis.grid(True,'minor', linewidth=0.5)
    
    # ax1.xaxis.grid(True,'major', linewidth =2)
    # ax1.xaxis.grid(True,'minor')
    ax1.yaxis.set_major_locator(MultipleLocator(10))
    ax1.yaxis.set_minor_locator(MultipleLocator(1))
    ax1.yaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'major', linewidth=0.5)
    ax2.yaxis.set_major_locator(MultipleLocator(10))
    ax2.yaxis.set_minor_locator(MultipleLocator(1))
    ax2.yaxis.grid(True,'major', linewidth=1)
    ax2.yaxis.grid(True,'major', linewidth=0.5)

    

    #Configure Labels and Title
    ax1.set_xlabel('PPS Increment')
    ax1.set_ylabel('UTC PPS Offset [ns]', size=12)
    ax2.set_ylabel('Frequency Error Estimate [ppb]', size=12)
    title = 'Pulse-Per-Second & Frequency Error Estimate'
    title += '\nLC_XO Serial: {:s}'.format(df.name)
    ax1.set_title(title)

    #Plot PPS & FEE Data
    ax1.plot(df['1PPS Count'], df['UTC offset ns'], 
             color='blue', linestyle = '-',linewidth=0.5,label='PPS UTC Offset [ns]')
    ax1.plot(df['1PPS Count'], df['PPS_SMA'], 
             color='blue', linestyle = '--',linewidth=0.5,label="PPS_SMA")
    ax2.plot(df['1PPS Count'], df['FEE_PPB'], 
             color='red', linestyle = '-', linewidth=0.5,label='FEE [ppb]')
    ax2.plot(df['1PPS Count'], df['FEE_SMA'], 
             color='red', linestyle = '--',linewidth=0.5,label="FEE_SMA")
    #ax1.plot(df['1PPS Count'], df['Frequency Error Estimate'])

    #Info Textbox
    # info =  "       mean [ppb]: {:3.3f}\n".format(df['FEE_PPB'].mean())
    # info += "       std  [ppb]: {:3.3f}\n".format(df['FEE_PPB'].std())
    # info += "       var  [ppb]: {:3.3f}\n".format(df['FEE_PPB'].var())
    # info += " Data Point Count: {:d}".format(len(df))
    # props = dict(boxstyle='round', facecolor='wheat', alpha=0.75)
    # ax1.text(0.5, 0.85, info, transform=ax1.transAxes, fontsize=12,
    #         verticalalignment='bottom', horizontalalignment='left',
    #         bbox=props, fontfamily='monospace')

    box = ax1.get_position()
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc='upper right')#, bbox_to_anchor=(.8, .5))
    ax1.legend(h1+h2, l1+l2, loc='upper right', bbox_to_anchor=(1, 1))
    # ax1.legend(h1, l1, loc='upper left', bbox_to_anchor=(.8, 1), prop={'size':10})

    plt.show()
    #plt.close(fig1)
    idx += 1
    return idx
