#!/usr/bin/env python
#################################################
#   Title: VCC Network Scheduler
# Project: Virginia Cubesat Constellation
# Version: 0.0.1
#    Date: Dec, 2019
#  Author: Zach Leffke, KJ4QLP
# Comment:
# - Imports Combined Pass File
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
    inf = parser.add_argument_group('Input File Configurations')
    inf.add_argument('--in_path',
                       dest='in_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'output']),
                       help="Input File Path",
                       action="store")
    inf.add_argument('--in_file',
                       dest='in_file',
                       type=str,
                       default="VCC_Network_Passes_20191201_20191217.csv",
                       help="Network Passes Input File Base Name",
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
                       default="VCC_Network_Passes_Reduced",
                       help="Network Passes Output File Base Name",
                       action="store")
    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------
    import warnings
    warnings.filterwarnings('ignore')
    os.system('reset')

    #check input file path
    if not os.path.exists(args.in_path):
        print 'ERROR: Invalid Input File Path: {:s}'.format(args.in_path)
        sys.exit()
    in_fp = "/".join([args.in_path, args.in_file])
    if not os.path.isfile(in_fp):
        print 'ERROR: Invalid File Name: {:s}'.format(args.in_file)
        sys.exit()
    #import data
    print "Importing File: {:s}".format(in_fp)
    df = pd.DataFrame.from_csv(in_fp, index_col="Network Pass #")
    df['Start Time (UTCG)'] = pd.to_datetime(df['Start Time (UTCG)'])
    df['Stop Time (UTCG)'] = pd.to_datetime(df['Stop Time (UTCG)'])
    print len(df)

    passes = {
        "GS Name":[],
        "SC Name":[],
        "SC NORAD ID": [],
        "Start Time (UTCG)":[],
        "Stop Time (UTCG)":[],
        "Duration (sec)":[],
        "Max El (deg)":[]
    }
    i=0
    while i < len(df):
        row = df.iloc[i]
        net_start = row['Start Time (UTCG)']
        net_stop = row['Stop Time (UTCG)']
        sc_name = row['SC Name']
        norad_id = row['SC NORAD ID']
        max_el = row['Max El (deg)']
        try:
            next_row = df.iloc[i+1]
            if next_row['Start Time (UTCG)'] < row['Stop Time (UTCG)']:
                i += 1
                net_stop = next_row['Stop Time (UTCG)']
                sc_name = "{:s}/{:s}".format(sc_name, next_row['SC Name'])
                norad_id = "{:d}/{:d}".format(norad_id, next_row['SC NORAD ID'])
                max_el = "{:s}/{:s}".format("{:2.1f}".format(max_el),
                                              "{:2.1f}".format(next_row['Max El (deg)']))
            net_duration = (net_stop-net_start).total_seconds()
        except:
            pass
        i+=1
        passes['GS Name'].append('VCC-NET')
        passes['SC Name'].append(sc_name)
        passes['SC NORAD ID'].append(norad_id)
        passes['Start Time (UTCG)'].append(net_start)
        passes['Stop Time (UTCG)'].append(net_stop)
        passes['Duration (sec)'].append(net_duration)
        passes['Max El (deg)'].append(max_el)

    passes_df = pd.DataFrame.from_dict(passes)
    passes_df = passes_df.sort_values('Start Time (UTCG)')
    passes_df = passes_df.reset_index(drop=True)
    print passes_df

    #setup output file information
    if not os.path.exists(args.out_path):
        print "creating: {:s}".format(args.out_path)
        os.makedirs(args.out_path)
    start = passes_df['Start Time (UTCG)'].iloc[0].strftime("%Y%m%d")
    stop  = passes_df['Stop Time (UTCG)'].iloc[-1].strftime("%Y%m%d")
    out_fn = "_".join([args.out_file,start,stop])
    out_fn = ".".join([out_fn, "csv"])
    #out_fn_net = "_".join([args.of_net,start,stop])
    #out_fn_net = ".".join([out_fn_net, "csv"])
    out_fp = "/".join([args.out_path, out_fn])
    print 'Exporting To File: {:s}'.format(out_fp)
    #cols = ["GS Name", "SC Name", "SC NORAD ID", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)", "Max El (deg)"]
    cols = ["GS Name", "SC Name", "SC NORAD ID", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)"]
    passes_df.to_csv(out_fp, columns=cols, index_label="Network Pass #")
    sys.exit()


if __name__ == '__main__':
    main()
