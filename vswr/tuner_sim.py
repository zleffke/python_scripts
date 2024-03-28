#!/usr/bin/env python3
'''
  Title: Tuner Simulation
Project: Antenna Modelling
   Date: Mar 2024
   Desc: Simulated Antenna Tuner, VSWR, etc.
  Input: Config File or user input
 Output: CSV, plotting
 Author: Zach Leffke, KJ4QLP

Useful Reference:
ARRL Radio Handbook
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


from utilities import plotting as plt
from utilities import pyvswr


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
    print(cfg)