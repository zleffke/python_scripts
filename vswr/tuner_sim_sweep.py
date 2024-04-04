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
    # Z_ant = complex(real=73, imag=42)

    #Antenna Complex Impedance, Folded Dipole
    Z_ant = complex(real=250, imag=50)

    #Power out of radio [Watts]
    P_tx = 1.0

    C1 = np.arange(1e-12,30e-12,1e-12)
    C2 = np.arange(1e-12,30e-12,1e-12)
    L  = np.arange(1e-9, 30.1e-9,1e-9)
    
    f_C = np.vectorize(rt.capacitor_impedance, excluded="f")
    f_L = np.vectorize(rt.inductor_impedance, excluded="f")
    X_c1 = f_C(C1, f_0)
    X_c2 = f_C(C2, f_0)
    X_2L = f_L(2*L, f_0)
    
    buff=np.array(np.meshgrid(X_c1,X_c2,X_2L)).T.reshape(-1,3)
    # buff=np.array(np.meshgrid(X_c1,X_c2)).T.reshape(-1,2)
    # print(X_c1[0], X_c2[0])
    print(len(buff))

    f_tee_tuner = np.vectorize(rt.tee_tuner, excluded=["Z_ant"])
    # X_eq = rt.tee_tuner_vec(buff[0], Z_ant)
    X_eq = f_tee_tuner(X_c1=buff[:,0], 
                       X_c2=buff[:,1], 
                       X_2L=buff[:,2], 
                       Z_ant=Z_ant)
    # print(X_eq)
    # print(len(X_eq))
    # X_df = pd.DataFrame(X_eq, columns=["X_eq"])

    df = pd.DataFrame(buff, columns=['X_C1', 'X_C2', 'X_2L'])
    # X_df['X_eq']=X_eq
    df['C1']=rt.xc_to_capacitance(df['X_C1'], f_0)
    df['C2']=rt.xc_to_capacitance(df['X_C2'], f_0)
    df['L'] =rt.x2l_to_inductance(df['X_2L'], f_0)
    df['X_eq'] = rt.tee_tuner(df['X_C1'],df['X_C2'],df['X_2L'], Z_ant)
    df['vswr'], df['Gamma'], df['rho'] = rt.vswr_impedance(df['X_eq'], Z_src)
    df['rl'], df['RL']=rt.return_loss_rho(df['rho'])
    df['P_rev'] = rt.power_reflected(df['rl'],P_tx)
    df['P_fwd'] = P_tx - df['P_rev']
    df['P_tx'] = df['P_fwd'] + df['P_rev']
    df['TX%'] = df['P_fwd'] / P_tx * 100
    df['REV%'] = df['P_rev'] / P_tx * 100
    # print(df)
    
    print(df['vswr'].min(), df['vswr'].idxmin())

    global_min_idx = df['vswr'].idxmin()
    print(global_min_idx)
    print(df.iloc[[global_min_idx]])
    L  = rt.x2l_to_inductance(df.iloc[[global_min_idx]]['X_2L'], f_0)
    C1 = rt.xc_to_capacitance(df.iloc[[global_min_idx]]['X_C1'], f_0)
    C2 = rt.xc_to_capacitance(df.iloc[[global_min_idx]]['X_C2'], f_0)
    vswr_max =df['vswr'].max()
    print("   Inductor for minimum VSWR: {:3.3f} nH".format(L[0]*1e9))
    print("Capacitor 1 for minimum VSWR: {:3.3f} pf".format(C1[0]*1e12))
    print("Capacitor 2 for minimum VSWR: {:3.3f} pf".format(C2[0]*1e12))

    # df_new = df[df['X_2L'] == df.iloc[global_min_idx]['X_2L']]
    # df_new.reset_index(inplace=True, drop=True)
    # df_new.name={
    #     "L": L[0]*1e9,
    #     "C1": C1[0]*1e12,
    #     "C2": C2[0]*1e12
    # }
    
    # print(df_new, len(df_new))    
    # plt.plot_vswr_multi(df)
    #plt.plot_vswr_heatmap(df_new)
    for idx,x2l in enumerate(pd.unique(df['X_2L'])):
        df_new = df[df['X_2L'] == x2l]
        df_new.reset_index(inplace=True, drop=True)
        # print(df_new)
        vswr_min = df_new['vswr'].min()
        idx_min = df_new['vswr'].idxmin()
        # print(idx, idx_min, vswr_min)

        L  = rt.x2l_to_inductance(df_new.iloc[[idx_min]]['X_2L'], f_0)[0]
        C1 = rt.xc_to_capacitance(df_new.iloc[[idx_min]]['X_C1'], f_0)[0]
        C2 = rt.xc_to_capacitance(df_new.iloc[[idx_min]]['X_C2'], f_0)[0]
        
        
        df_new.name={
            "L": L*1e9,
            "C1": C1*1e12,
            "C2": C2*1e12,
            "vswr_min":vswr_min,
            "vswr_max":vswr_max
        }
        print(df_new.name)
        plt.plot_vswr_heatmap(df_new, save=1)
        # plt.plot_Pfwd_heatmap(df_new)

    sys.exit()

    print(X_c1,X_c2, X_2L)
    print(len(X_c1), len(X_c2), len(X_2L))

    X_p1 = 1/((1)/(X_2L) + (1)/(X_c2+Z_ant))
    X_p2 = X_c1 + 1/((1)/(X_2L)+(1)/(X_p1))

    vswr = np.zeros((len(X_p1), len(X_p2), len(X_2L)), dtype=float)
    Gamma= np.zeros((len(X_p1), len(X_p2), len(X_2L)), dtype=complex)
    rho  = np.zeros((len(X_p1), len(X_p2), len(X_2L)), dtype=float)
    rl  = np.zeros((len(X_p1), len(X_p2), len(X_2L)), dtype=float)
    print(np.shape(buff))
    for a,xc1 in enumerate(X_c1):
        for b,xc2 in enumerate(X_c2):
            for c, xl in enumerate(X_2L):
                # print(a,b,c)
                # print(xc1,xc2,xl)
                X_p1 = 1/((1)/(xl) + (1)/(xc2+Z_ant))
                X_p2 = xc1 + 1/((1)/(xl)+(1)/(X_p1))
                vswr, Gamma, rho = rt.vswr_impedance(X_p2, Z_src)
                buff[a,b,c]=X_p2

    print(buff)




    sys.exit()

    while 1:
        rt.print_tuner_tee_schematic()
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

