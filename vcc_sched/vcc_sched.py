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
    cfg = parser.add_argument_group('Daemon Configuration File')
    cfg.add_argument('--cfg_path',
                       dest='cfg_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'input']),
                       help="Daemon Configuration File Path",
                       action="store")
    cfg.add_argument('--cfg_file',
                       dest='cfg_file',
                       type=str,
                       default="vtgs_wj2xms_vcc-b_44431_aer.csv",
                       help="AER File",
                       action="store")

    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------
    os.system('reset')
    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    print (fp_cfg)
    sys.exit()
    # if not os.path.isfile(fp_cfg) == True:
    #     print 'ERROR: Invalid Configuration File: {:s}'.format(fp_cfg)
    #     sys.exit()
    # print 'Importing configuration File: {:s}'.format(fp_cfg)
    # with open(fp_cfg, 'r') as json_data:
    #     cfg = json.load(json_data)
    #     json_data.close()
    # cfg['startup_ts'] = startup_ts
    #
    # log_name = '.'.join([cfg['ssid'],cfg['daemon_name'],'main'])
    # cfg['main_log'].update({
    #     "path":cfg['log_path'],
    #     "name":log_name,
    #     "startup_ts":startup_ts
    # })
    #
    # for key in cfg['thread_enable'].keys():
    #
    #     log_name =  '.'.join([cfg['ssid'],cfg['daemon_name'],cfg[key]['name']])
    #     cfg[key].update({
    #         'ssid':cfg['ssid'],
    #         'main_log':cfg['main_log']['name']
    #     })
    #     cfg[key]['log'].update({
    #         'path':cfg['log_path'],
    #         'name':log_name,
    #         'startup_ts':startup_ts,
    #         'level':cfg['main_log']['level']
    #     })
    #
    # print json.dumps(cfg, indent=4)
    #
    # main_thread = Main_Thread(cfg, name="Main_Thread")
    # main_thread.daemon = True
    # main_thread.run()
    # sys.exit()


if __name__ == '__main__':
    main()
