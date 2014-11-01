import numpy as np #vectores, operaciones matematicas
import time #hora local 
from configuration import GENERAL_CONFIG as CONFIG
#import os 
from multiprocess_config import *
#from configuration import DATA_FRAME_CONFIG as COMM
from configuration import FILE_CONFIG
from importlib import import_module
import logging
from os import path
from os import makedirs


if not path.exists('Logs'):
    makedirs('Logs')


logging.basicConfig(filename = 'Logs/data_bci.log', level = logging.WARNING)



def connect():
    """Retorna el dispositivo o una excepcion si falla"""
    from ok import okapi
    # find our device
    dev = okapi.OpalKelly()
    dev.reset()
    return dev


def get_data_from_file(com, send_warnings, cola):
    """Lee archivos y los envia al resto de los programas simulando ser online"""
    Parser =  getattr(import_module("Parsers."+CONFIG["FORMAT"]),"Parser")
    save_data = False
    reg_files = FileHandle()
    parser = Parser(cola,logging,data_in)
    comando = 'normal'
    extra_data = 0

    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo

            extra_data = parser.offline_update()
            if extra_data == 0: #estoy justo o me sobran datos    
                try:
                    time.sleep(CONFIG['PAQ_USB'] / CONFIG['FS'])
                    cola.put(parser.data, timeout = TIMEOUT_PUT)
                except Queue_Full:
                    try:
                        send_warnings.put_nowait([SLOW_PROCESS_SIGNAL])
                    except Queue_Full:
                        logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                if save_data:
                    reg_files.save(parser.data)

        comando = com.recv()
        save_data = (comando == START_SIGNAL)
        reg_files.actions(comando)
        


def get_data(com, send_warnings, dev, cola):
    """lee datos del USB, los reagrupa en una matriz de muestras y los envia por el buffer.
    Si se le envia la segnal los guarda"""
    Parser =  getattr(import_module("Parsers."+CONFIG["FORMAT"]),"Parser")
    save_data = False
    
    reg_files = FileHandle()
    parser = Parser(cola,logging,data_in)
    comando = 'normal'
    extra_data = 0
    dev.start(int(CONFIG['FS']))
  
    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo
            if (dev.data_available() >= 1000000):
                new_data = get_raw(extra_data)
                dev.read_data(new_data) #deberia ser N mas grande, si me faltan N tramas
                if save_data:
                    reg_files.save(new_data) 
                
                extra_data = parser.online_update(new_data)
                new_data = get_raw(extra_data)
                while extra_data <= 0: #estoy justo o me sobran datos
                    try:
                        cola.put(parser.data, timeout = TIMEOUT_PUT)
                    except Queue_Full:
                        try:
                            send_warnings.put_nowait([SLOW_PROCESS_SIGNAL])
                        except Queue_Full:
                            logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                    if extra_data < 0: #sobraban datos
                        extra_data = parser.online_update(new_data) 
                        new_data = get_raw(extra_data)
                    else:
                        break
            else :
                time.sleep(100 / CONFIG['FS'])
        comando = com.recv()
        save_data = (comando == START_SIGNAL)
        reg_files.actions(comando)
    dev.close();

class FileHandle():
    """Simplifica el guardado de archivos"""
    def __init__(self):
        #archivo cabecera
        self.paqxfile = FILE_CONFIG['MAX_SIZE_FILE']*2**20 /(
                        CONFIG['#CHANNELS']*CONFIG['PAQ_USB']*np.int16().nbytes
                        )
        
        self.num_registro = -1

    def new(self):
        self.part = 1 #parte del registro todo corrido
        self.file_part = open(FILE_CONFIG['GENERIC_FILE'] +'-'+str(self.num_registro) + '-' +str(self.part), 'wb')
        self.paq_in_part = 0
        
    def save(self, data):
        
        if(self.paq_in_part < self.paqxfile):
            data.tofile(self.file_part)
            self.paq_in_part += 1
        else:
            self.file_part.close()
            self.part += 1
            self.file_part = open(FILE_CONFIG['GENERIC_FILE'] + '-' + str(self.num_registro) +'-' +str(self.part),'wb')
            data.tofile(self.file_part)
            
            self.paq_in_part = 0
    
    def actions(self, signal):
        """Interfaz para facilitar el envio de segniales"""
        self.close()
        if signal is START_SIGNAL:
            self.num_registro += 1
            self.new()
	elif signal is EXIT_SIGNAL:
            self.close()

    def close(self):
        """Cierra el ultimo archivo y guarda configuraciones.
        Puede seguir guardando luego, solo que se modifica el numero de registro"""
        if self.num_registro >= 0:
            from ConfigParser import ConfigParser
            config_parser=ConfigParser()
            newsection = 'GENERAL'
            config_parser.add_section(newsection)
            config_parser.set(newsection, 'fs', int(CONFIG['FS']))
            config_parser.set(newsection, 'channels', CONFIG['#CHANNELS'])
            config_parser.set(newsection, 'adc_scale', CONFIG['ADC_SCALE'])
            
#            newsection = 'DATA_FRAME'
#            config_parser.add_section(newsection)
#            config_parser.set(newsection, 'l_frame', COMM['L_FRAME'])
#            config_parser.set(newsection, 'channels_pos', COMM['CHANNELS_POS'])
#            config_parser.set(newsection, 'counter_pos', COMM['COUNTER_POS'])
#            config_parser.set(newsection, 'hash_pos', COMM['HASH_POS'])
#            config_parser.set(newsection, 'ampcount', COMM['AMPCOUNT'])
            
            newsection = 'DATA_INFO'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'files',self.part)
            config_parser.set(newsection,'date',time.asctime( time.localtime(time.time())))
            file_head = open(FILE_CONFIG['GENERIC_FILE'] +'-'+str(self.num_registro) + '-0','w')
            config_parser.write(file_head)
            file_head.close()
            self.file_part.close()
            
        
class data_in():
    """Estructua que se envia al siguiente proceso"""
    __slots__ = ['data_loss_cuts','spikes','channels']
    def __init__(self):
        self.data_loss_cuts = list()
        self.spikes = list()
        self.channels = np.ndarray([CONFIG['#CHANNELS'], CONFIG['PAQ_USB']],np.uint16) #estan sin signo!
        
        
