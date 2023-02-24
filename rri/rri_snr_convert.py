#!/usr/bin/env python3
'''
  Title: RRI SNR converter
Project: ePOP RRI to GNU Radio
   Date: Sep 2022
   Desc: Converts Float-32 SNRs to Timestamped CSV.
  Input: F32 SNR measurement, binary file
 Output: CSV
 Author: Zach Leffke

RRI Data From:
https://epop.phys.ucalgary.ca/data/
'''
import sys, os, copy
import argparse
import warnings
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import numpy as np
import json
import yaml
import h5py
warnings.filterwarnings("ignore")

import hdf5_utils as utils


def import_configs_yaml(args):
    ''' setup configuration data '''
    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    #print (fp_cfg)
    if not os.path.isfile(fp_cfg) == True:
        print('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
        sys.exit()
    print('Importing configuration File: {:s}'.format(fp_cfg))
    with open(fp_cfg, 'r') as yaml_file:
        cfg = yaml.safe_load(yaml_file)
        yaml_file.close()

    if cfg['main']['base_path'] == 'cwd':
        cfg['main']['base_path'] = os.getcwd()
    return cfg

if __name__ == '__main__':
    #--------START Command Line option parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="RRI to SigMF",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    cfg.add_argument('--cfg_path',
                       dest='cfg_path',
                       type=str,
                       default=cfg_fp_default,
                       help="Configuration File Path",
                       action="store")
    cfg.add_argument('--cfg_file',
                       dest='cfg_file',
                       type=str,
                       default="config.yaml",
                       help="Configuration File",
                       action="store")

    parser.add_argument("-s", dest = "save_fig", action = "store", type = int, default=0 , help = "Save Data, 0=No, 1=Yes")

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    #--Import and Parse Configuration File
    cfg = import_configs_yaml(args)
    conv = utils.HDF5_SigMF_Converter(cfg)
    metadata = conv.get_metadata()

    df = pd.DataFrame()
    # df['Ephemeris UTC [sec]']        = pd.DataFrame(metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'])
    ScenarioStart = metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'][0]
    ScenarioEnd   = metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'][-1]
    ScenarioLength = ScenarioEnd - ScenarioStart
    print(ScenarioStart, ScenarioEnd)
    print(ScenarioLength)

    fp_a = "/".join([cfg['main']['rri_path'],cfg['snr']['file_a']])
    fp_b = "/".join([cfg['main']['rri_path'],cfg['snr']['file_b']])

    print(fp_a)
    print(fp_b)

    if not os.path.exists(fp_a) == True:
        if self.verbose: print('  ERROR: RRI SNR file or path does not exist: {:s}'.format(fp_a))
        sys.exit()
    else: print("Found SNR File A: {:s}".format(fp_a))
    if not os.path.exists(fp_b) == True:
        if self.verbose: print('  ERROR: RRI SNR file or path does not exist: {:s}'.format(fp_b))
        sys.exit()
    else: print("Found SNR File B: {:s}".format(fp_b))

    snr_a = np.fromfile(fp_a, dtype=np.single)
    snr_a = snr_a[5:]
    snr_b = np.fromfile(fp_b, dtype=np.single)
    snr_b = snr_b[5:]
    samp_rate = cfg['snr']['samp_rate']

    print(len(snr_a)/samp_rate)
    print(len(snr_b)/samp_rate)
    ts_list = []
    if len(snr_a) < len(snr_b):
        for i in range(len(snr_a)):
            ts_list.append(ScenarioStart + i*(1.0/samp_rate))
    else:# len(snr_b) < len(snr_a):
        for i in range(len(snr_b)):
            ts_list.append(ScenarioStart + i*(1.0/samp_rate))
        # print(ts, snr_a[i], snr_b[i])
    # print(ScenarioEnd)

    print(len(ts_list), len(snr_a), len(snr_b))

    df['Ephemeris UTC [sec]'] = pd.DataFrame(ts_list)
    df['Dipole A SNR [dB]'] = snr_a[0:len(ts_list)]
    df['Dipole B SNR [dB]'] = snr_b[0:len(ts_list)]

    of = "_".join(list(cfg['main']['rri_file'].split('_')[0:4])) + "_SNR.csv"
    o_fp = "/".join([cfg['main']['rri_path'], of])
    print(o_fp)
    df.to_csv(o_fp)
    sys.exit()
