# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 02:23:03 2015

@author: fer
"""
import numpy as np
from ConfigParser import ConfigParser


class iibm_loader():
    def __init__(self,reg_filename):
        self.reg_filename = reg_filename
        config = ConfigParser()
        config.read(reg_filename+'-0')
        
        self.fs = config.getfloat('GENERAL', 'fs')
        self.adc_scale = config.getfloat('GENERAL', 'adc_scale')
        self.channels = config.getint('GENERAL', 'channels')
        
        self.nfiles = config.getint('DATA_INFO','files')
        self.samples4file = config.getint('DATA_INFO','samples4file')
        self.samples4lastfile = config.getint('DATA_INFO','samples4lastfile')
        self.total_samples = self.samples4file * (self.nfiles - 1) + self.samples4lastfile
   
   
        self.dict_config = {}
        for section in config.sections():
            self.dict_config[section] = {}
            for key, val in config.items(section):
                self.dict_config[section][key] = val
        
        
        
    def get_data(self,channels = 'all', beg_time = 0, final_time='end'):
        if channels == 'all':
            channels = np.range(self.channels)
        
        beg_sample = int(np.floor(beg_time* self.fs))
        if self.total_samples < beg_sample:
            raise NameError('beg_time out of data')
            
        beg_file = int(beg_sample/self.samples4file)
        rel_beg_sample = beg_sample - beg_file * self.samples4file
        
        if final_time == 'end':
            final_sample = self.total_samples
        else:
            final_sample = int(np.ceil(final_time* self.fs))
        
        if final_sample <= beg_sample:
            raise NameError('final < beginning')
        
        final_file = int(final_sample/self.samples4file)
        rel_final_sample = final_sample - final_file * self.samples4file
        data = np.ndarray([len(channels),final_sample-beg_sample])
        if beg_file != final_file:
           #inicio:
            new_file = self.reg_filename + "-" + str(beg_file+1) #plus 1, because data begun in 1
            new_data = np.fromfile(new_file,np.int16)
            data[:, :self.samples4file - rel_beg_sample] = new_data.reshape([self.channels,new_data.size/self.channels],order='F')[channels,rel_beg_sample:]
            writed_samples = self.samples4file - rel_beg_sample
             
            #final
            new_file = self.reg_filename + "-" + str(final_file+1)#plus 1, because data begun in 1
            new_data = np.fromfile(new_file,np.int16)
            data[:, -rel_final_sample:] = new_data.reshape([self.channels,new_data.size/self.channels],order='F')[channels, :rel_final_sample]
        else:
            new_file = self.reg_filename + "-" + str(beg_file+1) #plus 1, because data begun in 1
            new_data = np.fromfile(new_file,np.int16)
            data = new_data.reshape([self.channels,new_data.size/self.channels],order='F')[channels,rel_beg_sample:rel_final_sample]
            writed_samples = self.samples4file - rel_beg_sample
       
 
        for i in range(beg_file+1,final_file+1): #50
            new_file = self.reg_filename + "-" + str(i+1)#plus 1, because data begun in 1
            new_data = np.fromfile(new_file, np.int16)
            data[:, writed_samples:writed_samples + self.samples4file]  = self.adc_scale * new_data.reshape([self.channels, new_data.size/self.channels], order='F')[channels, :]
            
        return data
if __name__ == '__main__':

    record = iibm_loader('test')
    if record.dict_config["GENERAL"]['format']=='example_raw':
        record.channels+=1
