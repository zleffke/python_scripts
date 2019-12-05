#!/usr/bin/env python
#############################################
#   Title: STK related functions            #
# Project: VCC Network Scheduler            #
#    Date: Dec 2019                         #
#  Author: Zach Leffke, KJ4QLP              #
#############################################
import math
import string
import time
import sys
import csv
import os
import datetime
import json
import pandas as pd

def Compute_Passes(data, max_el):
    acc_df = data['acc_df']
    aer_df = data['aer_df']

    passes = {
        "GS Name":[],
        "SC Name":[],
        "SC NORAD ID": [],
        "Start Time (UTCG)":[],
        "Stop Time (UTCG)":[],
        "Duration (sec)":[],
        "Max El (deg)":[]
    }
    cols = ["GS Name", "SC Name", "SC NORAD ID", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)", "Max El (deg)"]

    #print len(acc_df)
    for i in range(len(acc_df)):
        df_row = acc_df.iloc[i]
        start = df_row['Start Time (UTCG)']
        stop  = df_row['Stop Time (UTCG)']
        #df = df[(df['closing_price'] >= 99) & (df['closing_price'] <= 101)]
        pass_df = aer_df[(aer_df['Time (UTCG)'] >= start) & (aer_df['Time (UTCG)'] <= stop)]
        pass_df = pass_df.reset_index(drop=True)
        #print pass_df.loc[pass_df['Elevation (deg)'].idxmax()]
        #start = pass_df['Time (UTCG)'].iloc[0]
        #stop = pass_df['Time (UTCG)'].iloc[-1]
        #duration = (stop - start).total_seconds()
        #print gs_name, sc_name, sc_norad_id, start, stop, duration, max_el
        passes['GS Name'].append(data['gs_name'])
        passes['SC Name'].append(data['sc_name'])
        passes['SC NORAD ID'].append(data['norad_id'])
        passes['Start Time (UTCG)'].append(pass_df['Time (UTCG)'].iloc[0])
        passes['Stop Time (UTCG)'].append(pass_df['Time (UTCG)'].iloc[-1])
        passes['Duration (sec)'].append((pass_df['Time (UTCG)'].iloc[-1]-pass_df['Time (UTCG)'].iloc[0]).total_seconds())
        passes['Max El (deg)'].append(pass_df['Elevation (deg)'].loc[pass_df['Elevation (deg)'].idxmax()])

    passes_df = pd.DataFrame.from_dict(passes)
    passes_df = passes_df[passes_df['Max El (deg)'] >= max_el]
    passes_df = passes_df.reset_index(drop=True)
    passes_df.name = "{:s}_{:s}_{:s}".format(data['gs_name'],data['sc_name'],data['norad_id'])
    return passes_df

def Get_File_Names(in_path):
    #Setup input file information
    #get all file names in the path
    in_files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        in_files.extend(filenames)
        #break
    for i, file in enumerate(in_files):
        in_files[i] = "/".join([in_path,file])
    acc_files = []
    aer_files = []
    for i, in_f in enumerate(in_files):
        if 'aer' in in_f: aer_files.append(in_f)
        if 'access' in in_f: acc_files.append(in_f)
    return acc_files, aer_files

def Parse_File_Info(file):
    data = file.split('/')[-1].split('_')
    file_info = {
        "type":data[0],
        "gs_name":data[1],
        "gs_call":data[2],
        "sc_name":data[3],
        "norad_id":data[4].split('.')[0],
    }
    return file_info

def Generate_Dict_Keys(files):
    dict_keys = []
    for f in files:
        fd = Parse_File_Info(f)
        dict_keys.append("{:s}_{:s}_{:s}_{:s}".format(fd['gs_name'].upper(),
                                                      fd['gs_call'].upper(),
                                                      fd['sc_name'].upper(),
                                                      fd['norad_id']))
    return dict_keys

def Generate_DataFrame_Name(fd):
    #fd = dictionary of file data
    name = "{:s}_{:s}_{:s}_{:s}".format(fd['type'].upper(),
                                        fd['gs_name'].upper(),
                                        fd['sc_name'].upper(),
                                        fd['norad_id'])
    return name

def Import_STK_AER(aer_fp):
    #input:  Path to STK generated AER report in CSV format
    #output: pandas dataframe containing the AER info
    #intermediate:  Convert CSV time stamp strings to datetime objects
    print 'Importing AER File: {:s}'.format(aer_fp)
    df = pd.DataFrame.from_csv(aer_fp, index_col=None)
    print "Converting AER time stamps to datetime objects....might take a sec..."
    df['Time (UTCG)'] = pd.to_datetime(df['Time (UTCG)'])
    df.name = Generate_DataFrame_Name(Parse_File_Info(aer_fp))
    return df

def Import_STK_Access(acc_fp):
    #input:  Path to STK generated Access report in CSV format
    #output: pandas dataframe containing the Access info
    #intermediate:  Convert CSV time stamp strings to datetime objects
    print 'Importing Access File: {:s}'.format(acc_fp)
    df = pd.DataFrame.from_csv(acc_fp, index_col='Access')
    df = df.reset_index()
    print "Converting Access time stamps to datetime objects...."
    df['Start Time (UTCG)'] = pd.to_datetime(df['Start Time (UTCG)'])
    df['Stop Time (UTCG)'] = pd.to_datetime(df['Stop Time (UTCG)'])
    df.name = Generate_DataFrame_Name(Parse_File_Info(acc_fp))
    return df
