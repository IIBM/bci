#!/usr/bin/python
# -*- coding: utf-8 -*-


"""Load onfiguration
Create structures that will be loaded by other modules
@author: Fernando J. Chaure
"""
from Graphics.bci_config_editor import config_editor


confi_tuple = config_editor()

if confi_tuple == None:
    GENERAL_CONFIG = None
else:
    CONFIG, save_file, CONFIG_PARSER = confi_tuple
    GENERAL_CONFIG = {
        'ONLINE_MODE' : CONFIG.getboolean('GENERAL', 'online_mode'),
        '#CHANNELS' : CONFIG.getint('GENERAL', 'channels'),
        'FS' : CONFIG.getfloat('GENERAL', 'fs'),
        'PAQ_USB' : CONFIG.getint('GENERAL', 'data_package'),
        'ADC_SCALE' : CONFIG.getfloat('GENERAL', 'adc_scale'),
        'FORMAT' : CONFIG.get('GENERAL', 'format'),
        'FILTERED' : CONFIG.getboolean('GENERAL', 'filtered'),
        'PROBES_CONFIG' : CONFIG.get('GENERAL', 'probes_config')
    }


    FILE_CONFIG = {
        'MAX_SIZE_FILE' : CONFIG.getint('FILE', 'max_size_file'),
        'GENERIC_FILE' : save_file,
    }

       
    LIBGRAPH_CONFIG = {
        'BEEP_FREQ' : CONFIG.get('GRAPHICS', 'beep_freq'),
        'FFT_RESOLUTION' : CONFIG.getint('GRAPHICS', 'fft_resolution'),
        'FFT_N' : CONFIG.getint('GRAPHICS', 'fft_n'),
        'FFT_L_PAQ' : CONFIG.getint('GRAPHICS', 'fft_l_paq'),
        'ROWS_DISPLAY' : CONFIG.getint('GRAPHICS', 'rows_display'),
        'TIME_SPIKE_COUNT' : CONFIG.getint('GRAPHICS', 'time_spike_count'),
        'DISPLAY_LIMY' : CONFIG.getint('GRAPHICS', 'display_limy'),
        'MAX_PAQ_DISPLAY' : CONFIG.getint('GRAPHICS', 'max_paq_display'),
        'TWO_WINDOWS' : CONFIG.getboolean('GRAPHICS', 'two_windows')
    }


    SIGNAL_PROCESSING_CONFIG = {
        'LENGTH_FILTER' : CONFIG.getint('SIGNAL_PROCESSING', 'length_filter'),
        'FMIN' : CONFIG.getfloat('SIGNAL_PROCESSING', 'fmin'),
        'FMAX' : CONFIG.getfloat('SIGNAL_PROCESSING', 'fmax'),
        'BAND_PASS' : CONFIG.getboolean('SIGNAL_PROCESSING', 'band_pass'),
        'WINDOW_TYPE' : CONFIG.get('SIGNAL_PROCESSING', 'window_type')      
    }

    BIO_CONFIG = {
        'SPIKE_DURATION' : CONFIG.getfloat('BIO', 'spike_duration')
    }
    
    if GENERAL_CONFIG['PROBES_CONFIG'] == 'Tetrode':
        ELEC_GROUP = 4
        PROBE_CONF_L = 'TeT'
        GROUP_LABEL  = 'Tetrode'
        
    elif GENERAL_CONFIG['PROBES_CONFIG'] == 'Stereotrode':
        ELEC_GROUP = 2
        PROBE_CONF_L = 'SteT' 
        GROUP_LABEL  = 'Stereotrode'
        
    else:
        ELEC_GROUP = 1
        PROBE_CONF_L = ''
        GROUP_LABEL  = 'Electrode'
    
    GENERAL_CONFIG['ELEC_GROUP'] = ELEC_GROUP
    LIBGRAPH_CONFIG['PROBE_CONF_L'] = PROBE_CONF_L
    LIBGRAPH_CONFIG['GROUP_LABEL'] = GROUP_LABEL