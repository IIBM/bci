from configuration import CONFIG_PARSER
from multiprocess_config import *
from configuration import GENERAL_CONFIG as CONFIG
from os import path
import numpy as np


 

LARGO_TRAMA = (int(CONFIG_PARSER["FORMAT_CONFIG"]["no_ch"]) + CONFIG['#CHANNELS'] ) * int(CONFIG_PARSER["FORMAT_CONFIG"]["byte4sample"])
DATA_FRAME_L = (int(CONFIG_PARSER["FORMAT_CONFIG"]["no_ch"]) + CONFIG['#CHANNELS'] )

file_input_name = path.join(CONFIG_PARSER["FOLDER"],CONFIG_PARSER["FORMAT_CONFIG"]["file_name"])

class Parser():
    """Une secciones de datos raw y crea la matriz que se pasara al siguiente proceso"""
    def __init__(self,send_warnings,logging,data_in):     
        #define como sera el inicio de la trama en funcion de la cantidad de canales
        self.logging =logging
        self.send_warnings = send_warnings
        self.file_input = open(file_input_name,'rb')
        self.data = data_in()
   
    def Error_mess(self, error_string):
        self.logging.error(Errors_Messages[COUNTER_ERROR])
        try:
            self.send_warnings.put_nowait([COUNTER_ERROR,1])
        except Queue_Full:
            self.logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
       
    def offline_update(self):
        try:
            self.new_data = np.fromfile(self.file_input,'B',CONFIG['PAQ_USB']*LARGO_TRAMA)
            data = np.fromstring(self.new_data, dtype='<i2')
            self.data.channels = data.reshape([DATA_FRAME_L , CONFIG['PAQ_USB']],order='F')[:-1,:]
            return 0
        except:
            
            return 1
