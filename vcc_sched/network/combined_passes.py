#!/usr/bin/env python
#################################################
#   Title: VCC Network Scheduler
# Project: Virginia Cubesat Constellation
# Version: 0.0.1
#    Date: Dec, 2019
#  Author: Zach Leffke, KJ4QLP
# Comment:
# - Generates all passes and exports a combined CSV file
# - Network Pass version
#################################################

import math
import string
import time
import sys
import csv
import os
import datetime
import argparse
import json
import pandas as pd
import utilities.stk

def main():
    """ Main entry point to start the service. """

    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="VCC Scheduler",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    out = parser.add_argument_group('Output File Configurations')
    parser.add_argument('--in_path',
                       dest='in_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'input']),
                       help="Input File Path",
                       action="store")
    parser.add_argument('--max_el',
                       dest='max_el',
                       type=float,
                       default=10.0,
                       help="Pass Maximum Elevation Filter [deg]",
                       action="store")
    out.add_argument('--out_path',
                       dest='out_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'output']),
                       help="Output File Path",
                       action="store")
    out.add_argument('--out_file',
                       dest='out_file',
                       type=str,
                       default="VCC_Combined_Passes",
                       help="Combined Individual Passes Output File Base Name",
                       action="store")
    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------
    import warnings
    warnings.filterwarnings('ignore')
    os.system('reset')

    #Get AER and Access File names
    acc_files, aer_files = utilities.stk.Get_File_Names(args.in_path)
    #sort alphabetically
    keys = utilities.stk.Generate_Dict_Keys(acc_files)
    keys.sort()

    #generate passes
    passes = []
    for j,k in enumerate(keys):
        acc_f = [i for i in acc_files if k.lower() in i][0]
        aer_f = [i for i in aer_files if k.lower() in i][0]
        #print k, acc_f, aer_f
        print "{:d}/{:d}: {:s}".format(j+1, len(keys), k)
        acc_df = utilities.stk.Import_STK_Access(acc_f)
        aer_df = utilities.stk.Import_STK_AER(aer_f)
        print acc_df.name, aer_df.name
        data = {
            "gs_name":acc_df.name.split("_")[1],
            "sc_name":acc_df.name.split("_")[2],
            "norad_id":acc_df.name.split("_")[3],
            "acc_df":acc_df,
            "aer_df":aer_df
        }
        pass_df = utilities.stk.Compute_Passes(data, args.max_el)
        print "{:s}, Number of passes above {:2.1f} [deg] max el: {:d}\n".format(pass_df.name, args.max_el, len(pass_df))
        #print pass_df
        passes.append(pass_df)

    print "Number of Pass DataFrames: {:d}".format(len(passes))

    #form single large dataframe
    df = pd.concat(passes)
    #sort according to AOS
    df = df.sort_values('Start Time (UTCG)')
    df = df.reset_index(drop=True)
    print df
    print "Total Number of individual passes: {:d}".format(len(df))


    #setup output path
    if not os.path.exists(args.out_path):
        print "creating: {:s}".format(args.out_path)
        os.makedirs(args.out_path)
    #Setup Output file names
    #get first and last time stamp dates to form file name
    start = df['Start Time (UTCG)'].iloc[0].strftime("%Y%m%d")
    stop  = df['Stop Time (UTCG)'].iloc[-1].strftime("%Y%m%d")
    out_fn = "_".join([args.out_file,start,stop])
    out_fn = ".".join([out_fn, "csv"])
    #out_fn_net = "_".join([args.of_net,start,stop])
    #out_fn_net = ".".join([out_fn_net, "csv"])
    out_fp = "/".join([args.out_path, out_fn])
    #out_fp_net = "/".join([args.out_path, out_fn_net])
    print "Combined Output File Name:", out_fn
    #print " Network Output File Name:", out_fn_net
    #Export Combined Individual Passes to CSV file
    print 'Exporting Combined Passes To File: {:s}'.format(out_fp)
    comb_cols = ["GS Name", "SC Name", "SC NORAD ID", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)", "Max El (deg)"]
    df.to_csv(out_fp, columns=comb_cols, index_label="Pass #")









    sys.exit()
    aer_fp = '/'.join([args.in_path,args.aer_file])
    acc_fp = '/'.join([args.in_path,args.acc_file])
    if not os.path.isfile(aer_fp) == True:
        print 'ERROR: Invalid AER File: {:s}'.format(aer_fp)
        sys.exit()
    if not os.path.isfile(acc_fp) == True:
        print 'ERROR: Invalid Access File: {:s}'.format(acc_fp)
        sys.exit()

    #setup output file information
    if not os.path.exists(args.out_path):
        print "creating: {:s}".format(args.out_path)
        os.makedirs(args.out_path)
    file_info = args.aer_file.split('_')[0:4]
    print file_info
    gs_name = file_info[0].upper()
    sc_name = file_info[2].upper()
    sc_norad_id = file_info[3]
    file_info.append("passes.csv")
    out_fp = "/".join([args.out_path, "_".join(file_info)])

    print 'Importing AER File: {:s}'.format(aer_fp)
    aer_df = pd.DataFrame.from_csv(aer_fp, index_col=None)
    print "Converting AER time stamps to datetime objects....might take a sec..."
    aer_df['Time (UTCG)'] = pd.to_datetime(aer_df['Time (UTCG)'])
    print 'Importing Access File: {:s}'.format(acc_fp)
    acc_df = pd.DataFrame.from_csv(acc_fp, index_col='Access')
    acc_df = acc_df.reset_index()
    acc_df['Start Time (UTCG)'] = pd.to_datetime(acc_df['Start Time (UTCG)'])
    acc_df['Stop Time (UTCG)'] = pd.to_datetime(acc_df['Stop Time (UTCG)'])
    #print acc_df
    sch_df = pd.DataFrame()
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
        start = pass_df['Time (UTCG)'].iloc[0]
        stop = pass_df['Time (UTCG)'].iloc[-1]
        duration = (stop - start).total_seconds()
        max_el = pass_df['Elevation (deg)'].loc[pass_df['Elevation (deg)'].idxmax()]
        #print gs_name, sc_name, sc_norad_id, start, stop, duration, max_el
        passes['GS Name'].append(gs_name)
        passes['SC Name'].append(sc_name)
        passes['SC NORAD ID'].append(sc_norad_id)
        passes['Start Time (UTCG)'].append(start)
        passes['Stop Time (UTCG)'].append(stop)
        passes['Duration (sec)'].append(duration)
        passes['Max El (deg)'].append(max_el)

    passes_df = pd.DataFrame.from_dict(passes)
    passes_df = passes_df[passes_df['Max El (deg)'] >= args.max_el]
    passes_df = passes_df.reset_index(drop=True)

    print passes_df
    print 'Exporting To File: {:s}'.format(out_fp)
    #passes_df.to_csv(out_fp, columns=cols, index_label="Pass")
    #passes_df.to_csv(out_fp, columns=cols, index_label="Pass #", date_format="%Y-%m-%dT%H:%M:%S.%fZ")
    passes_df.to_csv(out_fp, columns=cols, index_label="Pass #")

if __name__ == '__main__':
    main()
