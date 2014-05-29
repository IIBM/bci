#!/usr/bin/python
#Load onfiguration

from bci_config_editor import config

class general_config():
    ONLINE_MODE=config.getboolean('GENERAL','online_mode')
    CANT_CANALES = config.getint('GENERAL','channels')
    FS = config.getfloat('GENERAL','fs')
    PAQ_USB= config.getint('GENERAL','data_package')

class file_config():   
    MAX_SIZE_FILE = config.getint('FILE','max_size_file')

class libgraph_config():
    BEEP_FREQ = config.get('GRAPHICS','beep_freq')  
    FFT_L =config.getint('GRAPHICS','fft_l')  
    FFT_N =config.getint('GRAPHICS','fft_n')  
    FFT_L_PAQ =config.getint('GRAPHICS','fft_l_paq')  
    ROWS_DISPLAY =config.getint('GRAPHICS','rows_display')
    TIME_SPIKE_COUNT=config.getint('GRAPHICS','time_spike_count')
    DISPLAY_LIMY=config.getint('GRAPHICS','display_limy')
    MAX_PAQ_DISPLAY=config.getint('GRAPHICS','max_paq_display')
    TWO_WINDOWS =config.getboolean('GRAPHICS','two_windows')


class data_frame_config():
    L_TRAMA = config.getint('DATA_FRAME','l_trama')
    COUNTER_POS = config.getint('DATA_FRAME','counter_pos')
    CHANNELS_POS = config.getint('DATA_FRAME','channels_pos')
    HASH_POS = config.getint('DATA_FRAME','hash_pos')
    
class signal_processing_config():
    LENGTH_FILTER = config.getint('SIGNAL_PROCESSING','length_filter')
    FMIN = config.getfloat('SIGNAL_PROCESSING','fmin')  
    FMAX = config.getfloat('SIGNAL_PROCESSING','fmax')  
    HIGH_PASS=config.getboolean('SIGNAL_PROCESSING','HIGH_PASS')
    WINDOW_TYPE = config.get('SIGNAL_PROCESSING','window_type')  

class spikes_config():
    SPIKE_DURATION=config.getfloat('SPIKES','spike_duration')  
