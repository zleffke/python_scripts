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
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import numpy as np
import json
import yaml
import h5py

if sys.version_info.major == 3:
    unicode = str

def import_h5(cfg):
    print("Importing RRI Data...")
    rri_fp = '/'.join([cfg['main']['rri_path'],
                       cfg['main']['rri_file']])
    if not os.path.exists(rri_fp) == True:
        print('  ERROR: RRI file or path does not exist: {:s}'.format(rri_fp))
        sys.exit()
    print(rri_fp)
    hf = h5py.File(rri_fp, 'r')
    return hf

class HDF5_Converter(object):
    """
    REF: https://gist.github.com/ssomnath/e3cb824b76d6837ea0f95054e6189574
    """
    def __init__(self):
        pass


    def get_attr(self, h5_object, attr_name):
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

        if isinstance(att_val, np.bytes_) or isinstance(att_val, bytes):
            att_val = att_val.decode('utf-8')

        elif type(att_val) == np.ndarray:
            if sys.version_info.major == 3:
                if att_val.dtype.type in [np.bytes_, np.object_]:
                    att_val = np.array([str(x, 'utf-8') for x in att_val])

        return att_val

    def get_attributes(self, h5_object, attr_names=None):
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
                att_dict[attr] = self.get_attr(h5_object, attr)
            except KeyError:
                raise KeyError('%s is not an attribute of %s' % (str(attr), h5_object.name))

        return att_dict

    def clean_attributes(self, metadata):
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

        for key in attrs_to_delete:
            del metadata[key]

        return metadata

    def get_attrs_from_groups(self, parent):
        metadata_tree = dict()
        for item_name, obj in parent.items():
            print(item_name)
            if isinstance(obj, h5py.Group):
                temp = self.clean_attributes(self.get_attributes(obj))
                print(temp)
                sub_attrs = self.get_attrs_from_groups(obj)
                #print(sub_attrs)
                temp.update(sub_attrs)
                metadata_tree[item_name] = temp
            #print(metadata_tree)

        return metadata_tree

    def get_metadata(self, parent):
        metadata = self.get_attrs_from_groups(parent)
        metadata = self.clean_attributes(metadata)
        return metadata
