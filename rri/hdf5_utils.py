#!/usr/bin/env python3
'''
  Title: RRI HDF5 to SigMF Converter
Project: ePOP RRI to GNU Radio
   Date: Sep 2022
 Author: Zach Leffke, KJ4QLP

CREDIT WHERE ITS DUE:
Most of these HDF5 conversion functions are primarily from:
https://gist.github.com/ssomnath/e3cb824b76d6837ea0f95054e6189574
Functions may be modified for this specific project
'''
from __future__ import print_function, division, unicode_literals
import sys, os, copy
import argparse
import warnings
import datetime
from datetime import timedelta
import pytz
import pandas as pd
import numpy as np
import json
import yaml
import h5py

if sys.version_info.major == 3:
    unicode = str
#
# def import_h5(cfg):
#     print("Importing RRI Data...")
#     rri_fp = '/'.join([cfg['main']['rri_path'],
#                        cfg['main']['rri_file']])
#     if not os.path.exists(rri_fp) == True:
#         print('  ERROR: RRI file or path does not exist: {:s}'.format(rri_fp))
#         sys.exit()
#     print(rri_fp)
#     hf = h5py.File(rri_fp, 'r')
#     return hf

class HDF5_SigMF_Converter(object):
    """
    REF: https://gist.github.com/ssomnath/e3cb824b76d6837ea0f95054e6189574
    """
    #def __init__(self, h5_data=None):
    def __init__(self, cfg):
        self.cfg = cfg
        self.h5_data = None
        self.metadata = None
        self.radio_data = None

        try:
            self._import_h5()
        except Exception as e:
            print(e)
            return 0

        self._gen_sigmf_filename(verbose = True)

        self.RRI_SAMP_RATE_REAL    = 1.0 / 62500.33933
        self.RRI_SAMP_RATE_COMPLEX = self.RRI_SAMP_RATE_REAL / 2
        self.rd = []

    def _import_h5(self):
        print("Importing RRI Data...")
        rri_fp = '/'.join([self.cfg['main']['rri_path'],
                           self.cfg['main']['rri_file']])
        print("Import Filepath: {:s}".format(rri_fp))
        if not os.path.exists(rri_fp) == True:
            print('  ERROR: RRI file or path does not exist: {:s}'.format(rri_fp))
            sys.exit()
        h5 = h5py.File(rri_fp, 'r')
        self.h5_data = h5
        print("RRI Data Import Complete")

    def _get_attr(self, h5_object, attr_name):
        """
        Returns the attribute from the h5py object
        Parameters
        ----------
        h5_object : h5py.Dataset, h5py.Group or h5py.File object
            object whose attribute is desired
        attr_name : str
            Name of the attribute of interest
        Returns
        -------
        att_val : object
            value of attribute, in certain cases (byte strings or list of byte strings) reformatted to readily usable forms
        """
        if not isinstance(h5_object, (h5py.Dataset, h5py.Group, h5py.File)):
            raise TypeError('h5_object should be a h5py.Dataset, h5py.Group or h5py.File object')

        if not isinstance(attr_name, (str, unicode)):
            raise TypeError('attr_name should be a string')

        #if attr_name not in h5_object.attrs.keys():
        if attr_name not in list(h5_object.keys()):
            raise KeyError("'{}' is not an attribute in '{}'".format(attr_name, h5_object.name))

        att_val = None
        if 'Monopole' not in attr_name:
            att_val = h5_object[attr_name][:]
            if len(att_val) == 1:
                att_val = att_val[0]

        if isinstance(att_val, np.bytes_) or isinstance(att_val, bytes):
            att_val = att_val.decode('utf-8')

        elif type(att_val) == np.ndarray:
            if sys.version_info.major == 3:
                if att_val.dtype.type in [np.bytes_, np.object_]:
                    att_val = np.array([str(x, 'utf-8') for x in att_val])

        return att_val

    def _get_attributes(self, h5_object, attr_names=None):
        """
        Returns attribute associated with some DataSet.
        Parameters
        ----------
        h5_object : h5py.Dataset
            Dataset object reference.
        attr_names : string or list of strings, optional, default = all (DataSet.attrs).
            Name of attribute object to return.
        Returns
        -------
        Dictionary containing (name,value) pairs of attributes
        """
        #print(h5_object)
        if not isinstance(h5_object, (h5py.Dataset, h5py.Group, h5py.File)):
            raise TypeError('h5_object should be a h5py.Dataset, h5py.Group or h5py.File object')

        if attr_names is None:
            #attr_names = h5_object.attrs.keys()
            attr_names = list(h5_object.keys())
            #print(attr_names)
        else:
            if isinstance(attr_names, (str, unicode)):
                attr_names = [attr_names]
            if not isinstance(attr_names, (list, tuple)):
                raise TypeError('attr_names should be a string or list / tuple of strings')
            if not np.all([isinstance(x, (str, unicode)) for x in attr_names]):
                raise TypeError('attr_names should be a string or list / tuple of strings')

        att_dict = {}

        for attr in attr_names:
            try:
                #print(h5_object, attr)
                #att_dict[attr] = self.get_attr(h5_object, attr)
                att_dict[attr] = self._get_attr(h5_object, attr)
            except KeyError:
                raise KeyError('%s is not an attribute of %s' % (str(attr), h5_object.name))

        return att_dict

    def _clean_attributes(self, metadata):
        attrs_to_delete = []
        for key, val in metadata.items():
            if type(val) in [np.uint16, np.uint8, np.uint, np.uint32, np.int, np.int16, np.int32, np.int64]:
                metadata[key] = int(val)
            if type(val) in [np.float, np.float16, np.float32, np.float64]:
                metadata[key] = float(val)
            if type(val) in [np.bool, np.bool_]:
                metadata[key] = bool(val)
            if isinstance(val, np.ndarray):
                metadata[key] = val.tolist()
            if isinstance(val, h5py.Reference):
                attrs_to_delete.append(key)

            # if "Radio Data Monopole" in key:
            #     attrs_to_delete.append(key)
            #     print("deleting Radio Data key...")
            if "RRI Data" in key:
                attrs_to_delete.append(key)
                print("deleting RRI Data metadata...")

        for key in attrs_to_delete:
            del metadata[key]

        return metadata

    def _remove_radio_data(self, metadata):
        attrs_to_delete = []
        for key, val in metadata.items():
            if "Radio Data Monopole" in key:
                attrs_to_delete.append(key)
            if "RRI Packet Number" in key:
                attrs_to_delete.append(key)
        for key in attrs_to_delete:
            del metadata[key]
        return metadata

    def _get_attrs_from_groups(self, parent):
        metadata_tree = dict()
        for item_name, obj in parent.items():
            #print(item_name)
            if isinstance(obj, h5py.Group):
                temp = self._clean_attributes(self._get_attributes(obj))
                #print(temp)
                sub_attrs = self._get_attrs_from_groups(obj)
                #print(sub_attrs)
                temp.update(sub_attrs)
                metadata_tree[item_name] = temp
            #print(metadata_tree)

        return metadata_tree

    def _generate_utc_time(self):
        ts_key = 'Ephemeris MET (seconds since May 24, 1968)'
        met_epoch = datetime.datetime(1968, 5, 24, 0, 0, 0)
        met_epoch = met_epoch.replace(tzinfo=datetime.timezone.utc)
        utc_epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
        utc_epoch = utc_epoch.replace(tzinfo=datetime.timezone.utc)
        epoch_delta = utc_epoch.timestamp() - met_epoch.timestamp()
        met = np.array(self.metadata['CASSIOPE Ephemeris'][ts_key])
        utc = met - epoch_delta
        self.metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'] = utc.tolist()

    def _update_metadata(self, parent):
        metadata = self._get_attrs_from_groups(parent)
        metadata = self._clean_attributes(metadata)
        # metadata = self._remove_sigmf_fps['dipole1']radio_data(metadata)
        self.metadata = metadata

    def get_metadata(self, h5_data=None):
        print('Generating Metadata From HDF5 Data...')
        if h5_data != None:
            print("updating converter HDF5 Data")
            self.h5_data = h5_data
        self._update_metadata(self.h5_data)
        self._generate_utc_time()
        return self.metadata

    def get_radio_iq(self, export =False):
        print("Extracting and Converting IQ...")
        self.rd = self.h5_data["RRI Data"]
        if self.metadata['RRI Settings']['Data Format'] == "I1Q1I3Q3":
            i1 = np.array(self.rd['Radio Data Monopole 1 (mV)'], dtype=np.single)
            q1 = np.array(self.rd['Radio Data Monopole 2 (mV)'], dtype=np.single)
            i2 = np.array(self.rd['Radio Data Monopole 3 (mV)'], dtype=np.single)
            q2 = np.array(self.rd['Radio Data Monopole 4 (mV)'], dtype=np.single)

            i1[np.isnan(i1)] = 0
            q1[np.isnan(q1)] = 0
            i2[np.isnan(i2)] = 0
            q2[np.isnan(q2)] = 0
            #iq2[np.isnan(iq2)] = 0
            #print ("IQ1 Length: {:d}".format(len(iq1)))
            self.i1_flat = np.hstack(i1)
            self.q1_flat = np.hstack(q1)
            self.i2_flat = np.hstack(i2)
            self.q2_flat = np.hstack(q2)
            #iq2_flat = np.hstack(iq2)
            #iq1_cp = np.apply_along_axis(lambda args: [np.complex(*args), 3, iq1_flat])
            self.iq1 = np.vectorize(complex)(self.i1_flat,self.q1_flat).astype(dtype=np.csingle)
            self.iq2 = np.vectorize(complex)(self.i2_flat,self.q2_flat).astype(dtype=np.csingle)

            if export:
                print("Writing IQ to file...")

                print("Writing Channel A File: {:s}".format(self.sigmf_fps['A']['data']))
                with open(self.sigmf_fps['A']['data'], 'w') as f:
                    self.iq1.tofile(f, sep="")
                    f.close()
                print("Writing Channel B File: {:s}".format(self.sigmf_fps['B']['data']))
                with open(self.sigmf_fps['B']['data'], 'w') as f:
                    self.iq2.tofile(f, sep="")
                    f.close()

    def get_radio_meta(self):
        print("---- CASSIOPE Metadata ---------")
        utc_min = self.metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'][0]
        utc_max = self.metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'][-1]
        dt_min = datetime.datetime.fromtimestamp(utc_min, tz=pytz.UTC)
        dt_max = datetime.datetime.fromtimestamp(utc_max, tz=pytz.UTC)
        utc_dur = utc_max - utc_min
        print("     Start [UTC]:", dt_min.isoformat().replace("+00:00","Z"))
        print("      Stop [UTC]:", dt_max.isoformat().replace("+00:00","Z"))
        print("     Start [sec]:", utc_min)
        print("      Stop [sec]:", utc_max)
        print("   utc_dur [sec]:", utc_dur)

        print("---- RRI Metadata PACKET---------")
        print("keys:", list(self.rd.keys()))
        rri_pkt_idx_min = min(self.rd['RRI Packet Numbers'])
        rri_pkt_idx_max = max(self.rd['RRI Packet Numbers'])
        print("RRI Packet Number:", rri_pkt_idx_min, rri_pkt_idx_max)
        samps_per_packet = 29
        sample_count = rri_pkt_idx_max * samps_per_packet
        print("samp count:", sample_count)
        duration = self.RRI_SAMP_RATE_REAL * sample_count
        print("  duration:", duration)
        print("---- RRI Metadata SAMPLES---------")
        samp_count = len(self.iq1)
        print("samp count:", samp_count)
        samp_dur = self.RRI_SAMP_RATE_REAL * samp_count
        print("  samp_dur:", samp_dur)

        #Generate Sigmf File Names
        self._gen_sigmf_metadata(verbose=True)

    def _gen_sigmf_metadata(self, verbose = False):
        #Generate initial dict structure
        self.dp1_sigmf_meta = copy.deepcopy(self.cfg['sigmf'])
        self.dp2_sigmf_meta = copy.deepcopy(self.cfg['sigmf'])

        utc_min = self.metadata['CASSIOPE Ephemeris']['Ephemeris UTC [sec]'][0]
        dt_min = datetime.datetime.fromtimestamp(utc_min, tz=pytz.UTC)

        print(self.metadata['RRI Settings'])

        #----DIPOLE 1-----------------------------
        self.dp1_sigmf_meta['global']['core']['hw'] = self.dp1_sigmf_meta['global']['core']['hw'] + ",CHAN-A"
        self.dp1_sigmf_meta['captures']['core']['datetime'] = dt_min.isoformat().replace("+00:00","Z")
        self.dp1_sigmf_meta['captures']['core']['frequency'] = self.metadata['RRI Settings']['Start Frequency A (Hz)']
        if verbose:
            print("--- DIPOLE 1 METADATA ----")
            print(json.dumps(self.dp1_sigmf_meta, indent=4))
            print("--------------------------")

        #----DIPOLE 2-----------------------------
        self.dp2_sigmf_meta['global']['core']['hw'] = self.dp2_sigmf_meta['global']['core']['hw'] + ",CHAN-B"
        self.dp2_sigmf_meta['captures']['core']['datetime'] = dt_min.isoformat().replace("+00:00","Z")
        self.dp2_sigmf_meta['captures']['core']['frequency'] = self.metadata['RRI Settings']['Start Frequency B (Hz)']
        if verbose:
            print("--- DIPOLE 2 METADATA ----")
            print(json.dumps(self.dp2_sigmf_meta, indent=4))
            print("--------------------------")


    def _gen_sigmf_filename(self, verbose = False):

        self.sigmf_fps = {}
        self.sigmf_fps['A'] = {}
        self.sigmf_fps['B'] = {}

        fn_rri = self.cfg['main']['rri_file']
        fn_list = fn_rri.split("_")[0:4]
        fn1_list = copy.copy(fn_list)
        fn2_list = copy.copy(fn_list)
        fn1_list.insert(1,"CHAN-A")
        fn2_list.insert(1,"CHAN-B")
        fn_dp1_meta = ".".join(["_".join(fn1_list), "sigmf-meta"])
        fn_dp2_meta = ".".join(["_".join(fn2_list), "sigmf-meta"])
        fn_dp1_data = ".".join(["_".join(fn1_list), "sigmf-data"])
        fn_dp2_data = ".".join(["_".join(fn2_list), "sigmf-data"])

        self.sigmf_fps['A']['meta'] = '/'.join([self.cfg['main']['rri_path'],fn_dp1_meta])
        self.sigmf_fps['B']['meta'] = '/'.join([self.cfg['main']['rri_path'],fn_dp2_meta])
        self.sigmf_fps['A']['data'] = '/'.join([self.cfg['main']['rri_path'],fn_dp1_data])
        self.sigmf_fps['B']['data'] = '/'.join([self.cfg['main']['rri_path'],fn_dp2_data])

        if verbose:
            print("Generated SigMF Filepath Names:")
            print(fn_dp1_meta, fn_dp2_meta)
            print(fn_dp1_data, fn_dp2_data)
            print(json.dumps(self.sigmf_fps, indent=4))
