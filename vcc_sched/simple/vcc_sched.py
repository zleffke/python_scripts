#!/usr/bin/env python
#################################################
#   Title: VCC Scheduler
# Project: Virginia Cubesat Constellation
# Version: 0.0.1
#    Date: Dec, 2019
#  Author: Zach Leffke, KJ4QLP
# Comment:
# - Generates schedule for VCC passes
# - Simplified initial version
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

def main():
    """ Main entry point to start the service. """

    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="VCC Scheduler",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    #cfg = parser.add_argument_group('Daemon Configuration File')
    parser.add_argument('--in_path',
                       dest='in_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'input']),
                       help="Input File Path",
                       action="store")
    parser.add_argument('--out_path',
                       dest='out_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'output']),
                       help="Output File Path",
                       action="store")
    parser.add_argument('--aer_file',
                       dest='aer_file',
                       type=str,
                       default="vtgs_wj2xms_vcc-b_44431_aer.csv",
                       help="AER File",
                       action="store")
    parser.add_argument('--acc_file',
                       dest='acc_file',
                       type=str,
                       default="vtgs_wj2xms_vcc-b_44431_access.csv",
                       help="Access File",
                       action="store")
    parser.add_argument('--max_el',
                       dest='max_el',
                       type=float,
                       default=10.0,
                       help="Pass Maximum Elevation Filter [deg]",
                       action="store")
    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------
    import warnings
    warnings.filterwarnings('ignore')
    os.system('reset')

    #Setup input file information
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
