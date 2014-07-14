#!/usr/bin/python
"""Load onfiguration
Crea estructuras que luego seran cargadas especificamente 
por otros modulos.
"""
from bci_config_editor import config_editor, save_file


CONFIG = config_editor()

GENERAL_CONFIG = {
    'ONLINE_MODE' : CONFIG.getboolean('GENERAL', 'online_mode'),
    'CANT_CANALES' : CONFIG.getint('GENERAL', 'channels'),
    'FS' : CONFIG.getfloat('GENERAL', 'fs'),
    'PAQ_USB' : CONFIG.getint('GENERAL', 'data_package'),
    'ADC_SCALE' : CONFIG.getint('GENERAL', 'adc_scale')
}

FILE_CONFIG = {
    'MAX_SIZE_FILE' : CONFIG.getint('FILE', 'max_size_file'),
    'GENERIC_FILE' : save_file,
    'LOAD_FILE' : CONFIG.get('FILE', 'load_file')
}

   
LIBGRAPH_CONFIG = {
    'BEEP_FREQ' : CONFIG.get('GRAPHICS', 'beep_freq'),
    'FFT_L' : CONFIG.getint('GRAPHICS', 'fft_l'),
    'FFT_N' : CONFIG.getint('GRAPHICS', 'fft_n'),
    'FFT_L_PAQ' : CONFIG.getint('GRAPHICS', 'fft_l_paq'),
    'ROWS_DISPLAY' : CONFIG.getint('GRAPHICS', 'rows_display'),
    'TIME_SPIKE_COUNT' : CONFIG.getint('GRAPHICS', 'time_spike_count'),
    'DISPLAY_LIMY' : CONFIG.getint('GRAPHICS', 'display_limy'),
    'MAX_PAQ_DISPLAY' : CONFIG.getint('GRAPHICS', 'max_paq_display'),
    'TWO_WINDOWS' : CONFIG.getboolean('GRAPHICS', 'two_windows')
}

DATA_FRAME_CONFIG =  {
    'L_FRAME' : CONFIG.getint('DATA_FRAME', 'l_frame'),
    'COUNTER_POS' : CONFIG.getint('DATA_FRAME', 'counter_pos'),
    'CHANNELS_POS' : CONFIG.getint('DATA_FRAME', 'channels_pos'),
    'HASH_POS' : CONFIG.getint('DATA_FRAME', 'hash_pos'),
    'AMPCOUNT' : CONFIG.getint('DATA_FRAME', 'ampcount')
}


SIGNAL_PROCESSING_CONFIG = {
    'LENGTH_FILTER' : CONFIG.getint('SIGNAL_PROCESSING', 'length_filter'),
    'FMIN' : CONFIG.getfloat('SIGNAL_PROCESSING', 'fmin'),
    'FMAX' : CONFIG.getfloat('SIGNAL_PROCESSING', 'fmax'),
    'BAND_PASS' : CONFIG.getboolean('SIGNAL_PROCESSING', 'band_pass'),
    'WINDOW_TYPE' : CONFIG.get('SIGNAL_PROCESSING', 'window_type')      
}

SPIKE_CONFIG = {
    'SPIKE_DURATION' : CONFIG.getfloat('SPIKES', 'spike_duration') 
}

