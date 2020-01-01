#!/usr/bin/env python3
#############################################
#   Title: Simple GPSd Logger
# Project: GPS Logger
#    Date: Dec 2019
#  Author: Zach Leffke, KJ4QLP
#############################################

import sys
import os
import math
import string
import datetime
import argparse
import json
import socket

def main(options):
    print options

if __name__ == '__main__':
    """ Main entry point to start the service. """

    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="VCC Scheduler",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    #sch_fp_default = '/'.join([cwd, 'schedule'])
    cfg_fp_default = '/'.join([cwd, 'config'])
    parser.add_argument("--cfg_fp"   ,
                        dest   = "cfg_path" ,
                        action = "store",
                        type   = str,
                        default=cfg_fp_default,
                        help   = 'config path')
    parser.add_argument("--cfg_file" ,
                        dest="cfg_file" ,
                        action = "store",
                        type = str,
                        default="gps_log_config.json" ,
                        help = 'config file')

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    cfg_fp = '/'.join([args.cfg_path, args.cfg_file])
    print ("config file:", cfg_fp)
    with open(cfg_fp, 'r') as cfg_f:
        cfg = json.loads(cfg_f.read())

    log_path = '/'.join([cfg['log']['path'],startup_ts])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serial = sock.makefile('r')
    sock.connect((cfg['gpsd']['ip'], cfg['gpsd']['port']))

    junk = serial.readline() # skip the daemon banner
    print (junk)
    sock.send('?WATCH={"enable":true,"nmea":false ,"json":true }\n\n')
    junk = serial.readline() # skip devices line
    print (junk)
    junk = serial.readline() # skip the "WATCH" line
    print (junk)

    while 1:
        outstr = serial.readline()
        print(outstr)
        junk = serial.readline() # skip the "WATCH" line
        print (junk)



    print (json.dumps(cfg,indent=4))
