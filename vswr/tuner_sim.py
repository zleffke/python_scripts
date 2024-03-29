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
from utilities import rf_tools as rt


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

    if cfg['base_path'] == 'cwd':
        cfg['base_path'] = os.getcwd()
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

    rt.print_tuner_tee_schematic()

    #frequency of operation
    f_0=915e6 #915 MHz

    #Transceiver complex impedance = 50 + 0j [Ohms]
    Z_src = complex(real=50, imag=0)

    #Antenna Complex Impedance, halfwave dipole at resonance
    Z_ant = complex(real=73, imag=42)

    #Capacitor 1, 1 picofarad
    C1 = 1e-12
    X_c1 = rt.capacitor_impedance(C1,f_0)
    #Capacitor 2, 1 picofarad
    C2 = 1e-12
    X_c2 = rt.capacitor_impedance(C2,f_0)
    #Inductor, 1 microhenry
    L=1e-6
    X_2L = rt.inductor_impedance(2*L, f_0)

    X_p1 = 1/(1/(X_2L) + 1/(X_c2+Z_ant))
    X_p2 = X_c1 + 1/((1)/(X_2L)+(1)/(X_p1))

    print(Z_src, Z_ant, X_c1, X_c2)
    print("X_p1", X_p1)
    print("X_p2", X_p2)

    vswr = rt.vswr_impedance(X_p2, Z_src)
    print("VSWR", vswr)    

    while 1:
        C1 = float(input("  C1 [f]:"))
        C2 = float(input("  C2 [f]:"))
        L  = float(input("   L [H]:"))
        P_tx = float(input("P_TX [W]:"))
        X_c1 = rt.capacitor_impedance(C1,f_0)
        X_c2 = rt.capacitor_impedance(C2,f_0)
        X_2L = rt.inductor_impedance(2*L, f_0)
        X_p1 = 1/((1)/(X_2L) + (1)/(X_c2+Z_ant))
        X_p2 = X_c1 + 1/((1)/(X_2L)+(1)/(X_p1))
        vswr, Gamma, rho = rt.vswr_impedance(X_p2, Z_src)
        rl,RL = rt.return_loss_rho(rho)
        P_rev = rt.power_reflected(rl,P_tx)
        P_fwd = P_tx - P_rev
        TX_percent = P_fwd / P_tx
        Refl_percent = 1-TX_percent
        print("       Z_src [Ohms]: {:.3f}".format(Z_src))
        print("       Z_ant [Ohms]: {:.3f}".format(Z_ant))
        print("       C1 [f], X_c1: {:.3E}, {:.3f}".format(C1, X_c1))
        print("       C2 [f], X_c2: {:.3E}, {:.3f}".format(C2, X_c2))
        print("        L [H], X_2L: {:.3E}, {:.3f}".format(L, X_2L))
        print("       X_p1  [Ohms]: {:.6f}".format(X_p1))
        print("       X_p2  [Ohms]: {:.6f}".format(X_p2))
        print("               VSWR:", vswr)    
        print("         Refl Coeff:", Gamma)
        print("                rho:", rho)
        print("   Return Loss [dB]:", RL)
        print("  return loss [lin]:", rl)
        print("Source TX Power [W]:", P_tx)
        print("     Transmission %:", TX_percent*100)
        print("        Reflected %:", Refl_percent*100)
        print("  Forward Power [W]:", P_fwd)
        print("  Reverse Power [W]:", P_rev)

