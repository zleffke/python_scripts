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
                       default='/'.join([os.getcwd(), 'output']),
                       help="Input File Path",
                       action="store")
    parser.add_argument('--out_path',
                       dest='out_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'output']),
                       help="Output File Path",
                       action="store")
    parser.add_argument('--out_fn',
                       dest='out_fn',
                       type=str,
                       default="VCC_Combined_Schedule_20191201-20191217.csv",
                       help="Output File Name",
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

    #get all file names in the path
    in_files = []
    for (dirpath, dirnames, filenames) in os.walk(args.in_path):
        in_files.extend(filenames)
        break
    for i, file in enumerate(in_files):
        in_files[i] = "/".join([args.in_path,file])
    print in_files

    #setup output file information
    if not os.path.exists(args.out_path):
        print "creating: {:s}".format(args.out_path)
        os.makedirs(args.out_path)
    out_fp = "/".join([args.out_path, args.out_fn])
    cols = ["GS Name", "SC Name", "SC NORAD ID", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)", "Max El (deg)"]

    #import the frames, convert to pandas dataframe
    frames = []
    print in_files
    for in_file in in_files:
        df = pd.DataFrame.from_csv(in_file, index_col="Pass #")
        frames.append(df)

    #Combine Data Frames, Sort in Ascending order by Start Time
    df = pd.concat(frames)
    df['Start Time (UTCG)'] = pd.to_datetime(df['Start Time (UTCG)'])
    df['Stop Time (UTCG)'] = pd.to_datetime(df['Stop Time (UTCG)'])
    df = df.sort_values('Start Time (UTCG)')
    df = df.reset_index(drop=True)
    print df
    print 'Exporting To File: {:s}'.format(out_fp)
    df.to_csv(out_fp, columns=cols, index_label="Pass #")

    sys.exit()


if __name__ == '__main__':
    main()
