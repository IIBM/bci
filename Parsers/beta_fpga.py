# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 17:28:58 2015

@author: fernando chaure
"""

from configuration import GENERAL_CONFIG as CONFIG
from multiprocess_config import *
import numpy as np
from configuration import CONFIG_PARSER
from os import path

COMM = {}
for x in CONFIG_PARSER['FORMAT_CONFIG']:
    if CONFIG_PARSER['FORMAT_CONFIG'][x].isdigit():
        COMM[x] = int(CONFIG_PARSER['FORMAT_CONFIG'][x])
    else:
        COMM[x] = CONFIG_PARSER['FORMAT_CONFIG'][x]

    
if not CONFIG['ONLINE_MODE']:
    if CONFIG_PARSER.has_key("DATA_INFO"):
        INFO = {}
        for x in CONFIG_PARSER['DATA_INFO']:
            if CONFIG_PARSER['DATA_INFO'][x].isdigit():
                INFO[x] = int(CONFIG_PARSER['DATA_INFO'][x])
            else:
                INFO[x] = CONFIG_PARSER['DATA_INFO'][x]
    from configuration import FILE_CONFIG
    
    
if path.exists(path.join(CONFIG_PARSER['FOLDER'],CONFIG_PARSER['FORMAT_CONFIG']['ch_order'])): #check if the string is a valid file name
    CH_ORD = np.loadtxt(path.join(CONFIG_PARSER['FOLDER'],CONFIG_PARSER['FORMAT_CONFIG']['ch_order']),np.int)-1
else: #else should be a list of ints
    CH_ORD = np.fromstring(CONFIG_PARSER['FORMAT_CONFIG']['ch_order'],np.int,sep=' ')-1
  
    
class Parser():
    """Une secciones de datos raw y crea la matriz que se pasara al siguiente proceso"""
    def __init__(self,send_warnings,logging,data_in):     
        #define como sera el inicio de la trama en funcion de la cantidad de canales
        dicc_aux = {1:'\x23''\xFF', 2:'\x46''\xFF'} #AUXILIAR

        self.FFplus = np.fromstring(dicc_aux[COMM['ampcount']], np.int16)
        self.logging = logging
        self.counter =- 1 #el counter de la trama
        self.frames_parsed = 0 #ubicacion en el bloque q se esta creando
        self.data = data_in()
        self.c_t = 0 #ubicacion en el bloque q se esta leyendo
        self.sinc = 0
        self.first_read = True
        self.send_warnings = send_warnings
        self.data_raw = np.ndarray(COMM['l_frame'] * CONFIG['PAQ_USB'] * 2, np.int16) #es el doble de grande que el que sera utilizado normalmente
        if not CONFIG['ONLINE_MODE']:
            self.open_file = None
            self.file_reading = FILE_CONFIG['FORMAT_FILE']
            self.unread_frames = 0
            self.n_file = 0
            
    def get_raw(self,extra_data):
        new_pack_data = (CONFIG['PAQ_USB'] + extra_data) * COMM['l_frame']
        return self.data_raw[:new_pack_data]  
    
    def online_update(self, data):
        """Recibe datos, los parsea. Si llena una trama fija retorna 0, 
        si faltan mas datos retorna cuantos, si sobran retorna -1"""
        max_c_t = data.size / COMM['l_frame']
        #si recien empieza con esos datos, primero sincroniza
        if self.c_t == 0 :
            self.sinc = 0
            while self.sinc < COMM['l_frame']:               
                if (data[self.sinc] == self.FFplus) and not( reduce(lambda x,y: x^y, data[self.sinc:self.sinc+ COMM['l_frame']])):
                    #parsea:
                    self.data.channels[:, self.frames_parsed] = (data[COMM['channels_pos'] + self.sinc:self.sinc+COMM['channels_pos'] + CONFIG['#CHANNELS']]-2**15)[CH_ORD]
                    self.frames_parsed += 1
                    counter_old = self.counter
                    self.counter = (data[COMM['counter_pos'] + self.sinc])
                    if np.int16(counter_old+1) != self.counter:
                        self.logging.error(Errors_Messages[COUNTER_ERROR])
                        try:
                            self.send_warnings.put_nowait([COUNTER_ERROR,1])
                        except Queue_Full:
                            self.logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                    #fin del priner parseo
                    break
                self.sinc += 1
            if(self.sinc >0 ):
                max_c_t = max_c_t-1
            if (self.sinc == COMM['l_frame']):
                self.logging.error(Errors_Messages[CANT_SYNCHRONIZE])
                try:
                    self.send_warnings.put_nowait([CANT_SYNCHRONIZE,CONFIG['PAQ_USB']])
                except Queue_Full:
                    self.logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                self.sinc =0
                self.c_t=0 #se concidera analizado y corrupto todo el paquete la proxima se empieza desde cero
                return CONFIG['PAQ_USB'] - self.frames_parsed
            else:
                self.c_t+=1
        #recorre hasta llenar tramas parseadas o parsear todo el bloque de datos crudos
        while self.frames_parsed < CONFIG['PAQ_USB'] and self.c_t < max_c_t:
            init_trama = self.c_t*COMM['l_frame']+self.sinc
            if(data[init_trama] != self.FFplus): #desincronizado
            #sinc=incronizar(c_t*40+sinc)# esto cambia c_t y s
                #print "desincronizacion detectada"
                self.logging.error(Errors_Messages[DATA_NONSYNCHRONIZED])
                try:
                    self.send_warnings.put_nowait([DATA_NONSYNCHRONIZED,CONFIG['PAQ_USB']-self.c_t])
                except Queue_Full:
                    self.logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])

                self.c_t = max_c_t #se concidera analizado y corrupto todo el paquete la proxima se empieza desde cero
                break
            #parsea:
            self.data.channels[:, self.frames_parsed] = (data[init_trama + COMM['channels_pos']:init_trama + COMM['channels_pos'] + CONFIG['#CHANNELS']]-2**15)[CH_ORD]
            #ojo aca se tendria q parsear y guardar el resto de la informacion q viene en la trama                
            self.frames_parsed += 1
            counter_old = self.counter
            self.counter = data[init_trama+COMM['counter_pos']]
            #comparo counteres aviso
            if np.int16(counter_old + 1) != self.counter:
                #guardo discontinuidad!!!
                #print "perdida de datos segun counter"
                self.logging.error(Errors_Messages[COUNTER_ERROR])
                try:
                    self.send_warnings.put_nowait([COUNTER_ERROR,1])
                except Queue_Full:
                    self.logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                
                
            #fin del parseo
  
            self.c_t += 1
            
        
        if self.frames_parsed == CONFIG['PAQ_USB']:
            self.frames_parsed = 0
            #retorno cuanto falta parsear del bloque crudo
            if self.c_t == max_c_t:
                self.c_t = 0 
                return 0
            else:
                #me sobra data puedo volver a update
                return -1

        else:
            #retorno cuanto le falta para terminar el bloque de canales
            self.c_t = 0
            return CONFIG['PAQ_USB'] - self.frames_parsed
            
            
    def offline_update(self):
        if (self.unread_frames == 0) and (self.n_file < INFO['files']):
            self.n_file = self.n_file+1
            self.open_file = open(FILE_CONFIG['FORMAT_FILE'][:-1]+str(self.n_file))
            if self.n_file == INFO['files']:
                self.unread_frames = INFO['samples4lastfile']
            else:
                self.unread_frames = INFO['samples4file']
        elif (self.unread_frames == 0) and (self.n_file == INFO['files']):
            return 1
            
        if self.unread_frames >= CONFIG['PAQ_USB']:
            self.new_data = np.fromfile(self.open_file,np.int16,CONFIG['PAQ_USB']*COMM['l_frame'])
            self.unread_frames = self.unread_frames -  CONFIG['PAQ_USB']
        else:
            self.new_data = np.fromfile(self.open_file,np.int16,self.unread_frames*COMM['l_frame'])
            self.unread_frames = 0
        
        if self.unread_frames == 0:
            self.open_file.close()

        return self.online_update(self.new_data)
