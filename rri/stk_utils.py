#!/usr/bin/env python3
'''
  Title: STK Utilities - STK
Project: RRI to STK Converter
   Date: Feb 2022
   Desc: Utility functions for generating
         STK formatted files
 Author: Zach Leffke, KJ4QLP
'''
from math import *
import string
import time
import sys
import csv
import os

import pandas as pd
import numpy as np
import datetime
import pytz

def export_STK_ephemeris(df, o_path):
    #--Exports single dataframe--
    #df    :  dataframe to export
    #o_path:  output path to FOLDER, need to append filename derived df name
    o_path += '/'+df.name+'.e'
    print("Ephemeris:", o_path)

    epoch = datetime.datetime.fromtimestamp(df['Ephemeris UTC [sec]'][0], tz=pytz.UTC)

    stk_header = _generate_STK_ephemeris_header(len(df), epoch)
    #print stk_header
    with open(o_path, 'w') as of:
        of.write(stk_header)
        of.close()

    header = ['Geographic Latitude (deg)','Geographic Longitude (deg)','Altitude (km)']
    df.to_csv(o_path, sep=' ', columns=header, header=False, mode='a')
    with open(o_path, 'a') as of:
        of.write('END Ephemeris')
        of.close()

def export_STK_attitude(df, o_path):
    #--Exports single dataframe--
    #df    :  dataframe to export
    #o_path:  output path to FOLDER, need to append filename derived df name
    o_path += '/'+df.name+'.a'
    print("Attitude:", o_path)
    epoch = datetime.datetime.fromtimestamp(df['Ephemeris UTC [sec]'][0], tz=pytz.UTC)
    stk_header = _generate_STK_attitude_header(len(df), epoch)
    #print stk_header
    with open(o_path, 'w') as of:
        of.write(stk_header)
        of.close()

    header = ['Yaw (deg)','Pitch (deg)','Roll (deg)']
    df.to_csv(o_path, sep=' ', columns=header, header=False, mode='a')
    with open(o_path, 'a') as of:
        of.write('END Attitude')
        of.close()

def _generate_STK_attitude_header(num_points, epoch):
    header = ''
    header += 'stk.v.5.0\n'
    header += 'BEGIN Attitude\n'
    # header += 'ScenarioEpoch            1 Jan 1970 00:00:00.000000000\n'
    header += 'ScenarioEpoch            {:s}\n'.format(epoch.strftime("%d %b %Y %H:%M:%S.%f"))
    header += 'NumberOfAttitudePoints   {:d}\n'.format(num_points)
    header += 'InterpolationOrder       1\n'
    header += 'CentralBody              Earth\n'
    header += 'CoordinateAxes           Fixed\n'
    header += 'Sequence                 321\n' #321 = Y-P-R
    header += 'AttitudeTimeYPRAngles\n'

    return header

def _generate_STK_ephemeris_header(num_points, epoch):
    header = ''
    header += 'stk.v.5.0\n'
    header += 'BEGIN Ephemeris\n'
    header += 'NumberOfEphemerisPoints  {:d}\n'.format(num_points)
    # header += 'ScenarioEpoch            1 Jan 1970 00:00:00.000000000\n'
    header += 'ScenarioEpoch            {:s}\n'.format(epoch.strftime("%d %b %Y %H:%M:%S.%f"))
    header += 'InterpolationMethod      Lagrange\n'
    header += 'InterpolationOrder       1\n'
    header += 'DistanceUnit             Kilometers\n'
    header += 'CentralBody              Earth\n'
    header += 'CoordinateSystem         Fixed\n'
    header += 'EphemerisLLATimePos\n'
    return header
