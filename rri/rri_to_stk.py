#!/usr/bin/env python3
'''
  Title: RRI HDF5 to SigMF Converter
Project: ePOP RRI to GNU Radio
   Date: Sep 2022
   Desc: Converts
  Input: Level 1 RRI Data, HDF5 Format
 Output: SigMF Record
 Author: Zach Leffke

using HDF5 conversion functions from:
https://gist.github.com/ssomnath/e3cb824b76d6837ea0f95054e6189574

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
import pandas as pd
warnings.filterwarnings("ignore")

import hdf5_utils as utils
import stk_utils as stk


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
    #print(cfg)
    #rri=utils.import_h5(cfg)
    #print(list(rri.keys()))
    #print(rri.keys())

    #conv = utils.HDF5_SigMF_Converter(rri)

    conv = utils.HDF5_SigMF_Converter(cfg)
    metadata = conv.get_metadata()

    df = pd.DataFrame()
    df['Ephemeris UTC [sec]']        = pd.DataFrame(metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'])
    # ScenarioEpoch = df['Ephemeris UTC [sec]'][0]
    # df['timestamp'] = df['Ephemeris UTC [sec]'] - ScenarioEpoch
    df['Geographic Latitude (deg)']  = metadata['CASSIOPE Ephemeris']['Geographic Latitude (deg)']
    df['Geographic Longitude (deg)'] = metadata['CASSIOPE Ephemeris']['Geographic Longitude (deg)']
    df['Altitude (km)']              = metadata['CASSIOPE Ephemeris']['Altitude (km)']
    df['Roll (deg)']                 = metadata['CASSIOPE Ephemeris']['Roll (deg)']
    df['Pitch (deg)']                = metadata['CASSIOPE Ephemeris']['Pitch (deg)']
    df['Yaw (deg)']                  = metadata['CASSIOPE Ephemeris']['Yaw (deg)']
    df.name = "_".join(cfg['main']['rri_file'].split("_")[0:4])
    print(df)
    print(metadata['CASSIOPE Ephemeris'].keys())
    # print(json.dumps(metadata.keys(), indent=4))

    # fn_base = "_".join(cfg['main']['rri_file'].split("_")[0:4])
    # fn_att = ".".join([fn_base, "a"])
    # fn_eph = ".".join([fn_base, "e"])
    # print(fn_base)
    # fp = cfg['main']['rri_path']
    # fp_att = "/".join([fp,fn_att])
    # fp_eph = "/".join([fp,fn_eph])

    if cfg['stk']['export']:
        stk.export_STK_ephemeris(df, cfg['main']['rri_path'])
        stk.export_STK_attitude(df, cfg['main']['rri_path'])

    sys.exit()
