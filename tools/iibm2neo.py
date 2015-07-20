# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 02:14:40 2015

@author: fer
"""

#!/usr/bin/python

import sys, getopt
from ConfigParser import ConfigParser
from neo import io
import quantities as pq
import numpy as np

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg


    config = ConfigParser()
    #cargo configuracion iibm
    
    try:
        config.read(inputfile)
    except:
        print 'inputfile should be a valid INI file'
        sys.exit(2)
    
    FS=30030.
    CHANNELS=25#?
    r = io.RawBinarySignalIO( filename = 'data_test')
    seg=r.read_segment(sampling_rate=FS * pq.Hz, t_start=0.0 * pq.s, 
                   unit=pq.V, nbchannel=CHANNELS, bytesoffset=0, dtype=np.int16,
                   rangemin=-10, rangemax=10)
    out_io = io.NeoHdf5IO('salida.hdf5')
    out_io.write_analogsignalarray(seg)
    
    #crea 
#     for i in range(15,28): #50
#        new_file = "210612_"+str(i)
#        new_data = np.fromfile(new_file,np.int16)
#        new_data = new_data.reshape([25,new_data.size/25],order='F')[TET*4:TET*4+4,:]
#        
#        
if __name__ == "__main__":
    main(sys.argv[1:])
    #    trasforma todos los registros, habria que agregar la opcion de 
    #recortarlos de alguna forma. Otro problea es el canal extra; se deberia agregar
    #un analisis aparte para, omitirtlo o agregarlo a neo
    