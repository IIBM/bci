# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 19:04:12 2015

@author: fer
"""
import numpy as np 
from configuration import GENERAL_CONFIG as CONFIG



class SpikeSortingHandler():
    def __init__(self, queue):
        self.queue = queue
        self.classification_status = np.zeros(CONFIG['#CHANNELS'])
        self.clustering_status = np.zeros(CONFIG['#CHANNELS'],dtype=bool)
        elec_groups = list()        
        for i in range(CONFIG['#CHANNELS']/CONFIG['ELEC_GROUP']):
            elec_groups.append(ElectGroupSpS())
            
            
    def update_conf(self, command):
        """Read the comment and configure clustering and classification."""
        
    def process_data(self, data, detected_times):
         """Process new data."""
        


class ElectGroupSpS():
    def __init__(self):
        self.detected_neurons = [0]
        
        
    def clustering(self, spikes, restart=False):
       """Process new data""" 
       
       
    def sort(self, data,detected_times,neurons):
        """return activation0 times of neurons""" 

