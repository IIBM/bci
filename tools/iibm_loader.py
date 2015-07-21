# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 02:23:03 2015

@author: fer
"""
import numpy as np
from ConfigParser import ConfigParser




class iibm_record():
    def __init__(self,ini_filename):
        config = ConfigParser()
        config.read(ini_filename)
        self.fs = config.getfloat('GENERAL', 'fs')
        self.adc_scale = config.getfloat('GENERAL', 'adc_scale')
        self.channels = config.getint('GENERAL', 'channels')
        self.nfiles = config.getint('DATA_INFO','files')
        #time4file
        #time4lastfile
        dict_config = {}
        for section in config.sections():
            dict_config[section] = {}
            for key, val in config.items(section):
                dict_config[section][key] = val
        
        
        
    def get_signals(self,channels='all', beg_time=0, final_time='end'):
        
if __name__ == '__main__':
    TET = 2
    data = np.ndarray([4,0])
    for i in range(15,28): #50
        new_file = "210612_"+str(i)
        new_data = np.fromfile(new_file,np.int16)
        new_data = new_data.reshape([25,new_data.size/25],order='F')[TET*4:TET*4+4,:]
        
        data = np.hstack([data,new_data])
