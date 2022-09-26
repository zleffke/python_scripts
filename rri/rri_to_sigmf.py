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
warnings.filterwarnings("ignore")

import hdf5_utils as utils


def import_configs_yaml(args):
    ''' setup configuration data '''
    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    print (fp_cfg)
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
    rri=utils.import_h5(cfg)
    print(list(rri.keys()))
    print(rri.attrs.keys())

    conv = utils.HDF5_Converter()
    metadata = conv.get_metadata(rri)
    #metadata = utils.clean_attributes(metadata)
    #print(metadata)
    for key in metadata.keys():
        print(metadata[key])



    sys.exit()




    meta = dict()
    for item_name, obj in rri.items():
        print(item_name)
        print(obj)
        if isinstance(obj, h5py.Group):
            temp = clean_attributes(get_attributes(obj))
            sub_attrs = get_attrs_from_groups(obj)
            temp.update(sub_attrs)
            metadata_tree[item_name] = temp

    sys.exit()






    for k in rri.keys():
        print(k)
        print(rri[k].keys())

    print(np.array(rri['RRI Data']['RRI Packet Numbers']))

    print(np.array(rri['RRI Data']['Radio Data Monopole 1 (mV)']))

    sys.exit()
