#!/usr/bin/env python3
#version 2.1

import socket
import os
import string
import sys
import time
import argparse
import datetime
import json
from scipy import signal
from binascii import *

if __name__ == '__main__':
    """ Main entry point to start the service. """
    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="M-Sequence Generator",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    parser.add_argument('--n',
                        dest='n',
                        type=int,
                        default=2,
                        help="M Sequence bits, length = 2^n-1",
                        action="store")
    parser.add_argument('--v',
                        dest='verbosity',
                        type=int,
                        default=0,
                        help="verbosity, 1 = True",
                        action="store")
    parser.add_argument('--w',
                        dest='write_file',
                        type=int,
                        default=0,
                        help="Write to File, 1 = True",
                        action="store")
    parser.add_argument('--file_name',
                        dest='file_name',
                        type=str,
                        default="mseq.dat",
                        help="Output file name",
                        action="store")
    args = parser.parse_args()
#--------END Command Line argument parser------------------------------------------------------
    print (args.n)
    m = signal.max_len_seq(args.n)
    print ("Sequence Length: {:d}".format(len(m[0])))
    if args.verbosity:
        print (m[0].tobytes())
    if args.write_file:
        fp = '/'.join([os.getcwd(), args.file_name])
        print (fp)
        with open(fp, 'w') as f:
            m[0].tofile(f)
        f.close()
