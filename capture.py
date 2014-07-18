import numpy as np #vectores, operaciones matematicas
import time #hora local 
from configuration import GENERAL_CONFIG as CONFIG
#import os 
#import array
from multiprocess_config import *
from configuration import DATA_FRAME_CONFIG as COMM
from configuration import FILE_CONFIG

import logging
logging.basicConfig(filename='data_bci.log',level=logging.WARNING)


def connect():
    import okapi
    # find our device
    dev = okapi.OpalKelly()
    dev.reset()
    return dev
   
def get_data_from_file(com,send_warnings,cola):
    save_data=False
    reg_files=file_handle()
    parser=Parser(cola)
    comando='normal'
    extra_data=0
    file_counter=0
    frame4file=0
    frame_counter=0
    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo
            if(frame_counter+1 >= frame4file):        
                file_counter+=1
                try:                
                    file_data=np.fromfile(FILE_CONFIG['LOAD_FILE']+str(file_counter),np.int16)
                except:
                    print "fin de archivos guardados"
                frame4file=file_data.size/COMM['L_FRAME']
                frame_counter=0
            #new_pack_data=(CONFIG['PAQ_USB']+extra_data)*COMM['L_FRAME'] cantidad en el proximo
            #data[:new_pack_data] aca van los nuevos
            if save_data:
                reg_files.save(file_data[COMM['L_FRAME']*frame_counter:(frame_counter+1)*COMM['L_FRAME']]) 
            
            extra_data=parser.update(file_data[COMM['L_FRAME']*frame_counter:(frame_counter+1)*COMM['L_FRAME']])
            frame_counter+=1
            if extra_data ==0: #estoy justo o me sobran datos    
                try:
                    time.sleep(CONFIG['PAQ_USB']/CONFIG['FS'])
                    cola.put(parser.data,timeout=TIMEOUT_PUT)
                except:
                    try:
                        send_warnings.put_nowait([SLOW_PROCESS_SIGNAL])
                    except:
                        logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
            
#            try:
#                time.sleep(1/CONFIG['FS']-(time.time()-sample_time))
#            except:
#                print "slow read file"
        comando=com.recv()
        save_data= (comando==START_SIGNAL)
	reg_files.actions(comando)



#def fake_file_obtener_datos(com,send_warnings,cola):
#    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
#    LARGO_TRAMA=2*CONFIG['CANT_CANALES']+2
#    reg_files=file_handle()
#    file_input=open('data_test','rb')
#    save_data=False
#    data2=data_in()
#    comando=''
#    while(comando != EXIT_SIGNAL):      
#        while not com.poll():
#            lectura_nueva=np.fromfile(file_input,'B',CONFIG['PAQ_USB']*LARGO_TRAMA)
#            data=np.fromstring(lectura_nueva, dtype='<i2')
#            new_data=data.reshape([CONFIG['CANT_CANALES']+1,CONFIG['PAQ_USB']],order='F')
#            data2.channels=new_data[:-1,:]
#            try:
#                cola.put_nowait(data2)
#            except:
#                try:
#                    send_warnings.put_nowait(SLOW_PROCESS_SIGNAL)
#                except:
#                    pass    
#            time.sleep(CONFIG['PAQ_USB']*0.9/CONFIG['FS'])
#            if save_data:
#                reg_files.save(lectura_nueva)
#            #agrega el largo del archivo
#        comando=com.recv()
#        reg_files.actions(comando)
#        save_data= comando=='guardar'
#    file_input.close()
     

def get_data(com,send_warnings,dev,cola):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer     
    
    save_data=False
    
    reg_files=file_handle()
    parser=Parser(cola)
    comando='normal'
    extra_data=0
    data=np.ndarray(COMM['L_FRAME']*CONFIG['PAQ_USB']*2,np.int16) #es el doble de grande que el que sera utilizado normalmente
    dev.start(int(CONFIG['FS']))

    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo
            if (dev.data_available() >= 1000000):
                # data es un array de numpy de uint16
                # n es un entero que tiene la cantidad de palabras de 16 bits transmitidas
                new_pack_data=(CONFIG['PAQ_USB']+extra_data)*COMM['L_FRAME']
                n = dev.read_data(data[:new_pack_data]) #deberia ser N mas grande, si me faltan N tramas
                if save_data:
                    reg_files.save(data[:new_pack_data]) 
                
                extra_data=parser.update(data[:new_pack_data])

                while extra_data <=0: #estoy justo o me sobran datos
                    try:
                        cola.put(parser.data,timeout=TIMEOUT_PUT)
                    except:
                        try:
                            send_warnings.put_nowait([SLOW_PROCESS_SIGNAL])
                        except:
                            logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                    if extra_data < 0: #sobraban datos
                        extra_data=parser.update(data[:new_pack_data]) 
                    else:
                        break
            else :
                time.sleep(100/CONFIG['FS'])
        comando=com.recv()
        save_data= (comando==START_SIGNAL)
	reg_files.actions(comando)
    dev.close();

class file_handle():
    def __init__(self):
        #archivo cabecera
        self.paqxfile=FILE_CONFIG['MAX_SIZE_FILE']*2**20/COMM['L_FRAME']/CONFIG['PAQ_USB']/np.int16().nbytes
        
        self.num_registro=-1

    def new(self):
        self.part=1 #parte del registro todo corrido
        
        self.file_part=open(FILE_CONFIG['GENERIC_FILE'] +'-'+str(self.num_registro) +'-' +str(self.part),'wb')
        
        self.paq_in_part=0
        
    def save(self,data):
        
        if(self.paq_in_part<self.paqxfile):
            data.tofile(self.file_part)
            self.paq_in_part+=1
        else:
            self.file_part.close()
            self.part+=1
            self.file_part=open(FILE_CONFIG['GENERIC_FILE'] +'-'+str(self.num_registro) +'-' +str(self.part),'wb')
            data.tofile(self.file_part)
            
            self.paq_in_part=0
    
    def actions(self,signal):
        self.close()
        if signal is START_SIGNAL:
            self.num_registro+=1
            self.new()
	elif signal is EXIT_SIGNAL:
            self.close()

    def close(self):
        if self.num_registro >= 0:
            from ConfigParser import ConfigParser
            config_parser=ConfigParser()
            newsection='GENERAL'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'fs',int(CONFIG['FS']))
            config_parser.set(newsection,'channels',CONFIG['CANT_CANALES'])
            config_parser.set(newsection,'adc_scale',CONFIG['ADC_SCALE'])
            
            newsection='DATA_FRAME'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'l_frame',COMM['L_FRAME'])
            config_parser.set(newsection,'channels_pos',COMM['CHANNELS_POS'])
            config_parser.set(newsection,'counter_pos',COMM['COUNTER_POS'])
            config_parser.set(newsection,'hash_pos',COMM['HASH_POS'])
            config_parser.set(newsection,'ampcount',COMM['AMPCOUNT'])
            
            newsection='DATA_INFO'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'files',self.part)
            config_parser.set(newsection,'date',time.asctime( time.localtime(time.time())))
            file_head= open(FILE_CONFIG['GENERIC_FILE'] +'-'+str(self.num_registro) + '-0','w')
            config_parser.write(file_head)
            file_head.close()
            self.file_part.close()
            
        
class data_in():
    def __init__(self):
        self.data_loss_cuts=list()
        self.spikes=list()
        self.channels=np.ndarray([CONFIG['CANT_CANALES'],CONFIG['PAQ_USB']],np.uint16) #estan sin signo!
        
        
class Parser():
    def __init__(self,send_warnings):     
        dicc_aux={1:'\x23''\xFF',2:'\x46''\xFF'} #AUXILIAR

        self.FFplus=np.fromstring(dicc_aux[COMM['AMPCOUNT']],np.int16)
        
        self.contador =- 1 #el contador de la trama
        self.tramas_parseadas = 0 #ubicacion en el bloque q se esta creando
        self.data = data_in()
        self.c_t = 0#ubicacion en el bloque q se esta leyendo
        self.sinc = 0
        self.first_read = True
        self.send_warnings = send_warnings
        
    def update(self,data):
        max_c_t=data.size/COMM['L_FRAME']
        #si recien empieza con esos datos, primero sincroniza
        if self.c_t==0 :
            self.sinc=0
            while self.sinc < COMM['L_FRAME']:               
                if (data[self.sinc] == self.FFplus) and not( reduce(lambda x,y: x^y, data[self.sinc:self.sinc+ COMM['L_FRAME']])):
                    #parsea:
                    self.data.channels[:,self.tramas_parseadas] = data[COMM['CHANNELS_POS']+self.sinc:self.sinc+COMM['CHANNELS_POS']+CONFIG['CANT_CANALES']]
                    self.tramas_parseadas += 1
                    contador_old = self.contador
                    self.contador = (data[COMM['COUNTER_POS']+self.sinc])
                    if np.int16(contador_old+1) != self.contador: #and not self.first_read:
                        #self.first_read=False
                        #guardo discontinuidad!!!
                        #print "perdida de datos segun contador"
                        logging.error(Errors_Messages[COUNTER_ERROR])
                        try:
                            self.send_warnings.put_nowait([COUNTER_ERROR,1])
                        except:
                            logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                    #fin del priner parseo
                    break
                self.sinc+=1
            if(self.sinc >0 ):
                max_c_t=max_c_t-1
            if (self.sinc == COMM['L_FRAME']):
                #print "se recorrio una trama y nunca se sincronizo"
                logging.error(Errors_Messages[CANT_SYNCHRONIZE])
                try:
                    self.send_warnings.put_nowait([CANT_SYNCHRONIZE,CONFIG['PAQ_USB']])
                except:
                    logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                #self.first_read=True
                self.sinc =0
                self.c_t=0 #se concidera analizado y corrupto todo el paquete la proxima se empieza desde cero
                return CONFIG['PAQ_USB'] - self.tramas_parseadas
            else:
                self.c_t+=1
        #recorre hasta llenar tramas parseadas o parsear todo el bloque de datos crudos
        while self.tramas_parseadas < CONFIG['PAQ_USB'] and self.c_t < max_c_t:
            init_trama=self.c_t*COMM['L_FRAME']+self.sinc
            if(data[init_trama] != self.FFplus): #desincronizado
            #sinc=incronizar(c_t*40+sinc)# esto cambia c_t y s
                #print "desincronizacion detectada"
                logging.error(Errors_Messages[DATA_NONSYNCHRONIZED])
                try:
                    self.send_warnings.put_nowait([DATA_NONSYNCHRONIZED,CONFIG['PAQ_USB']-self.c_t])
                except:
                    logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                #self.first_read=True
                self.c_t=max_c_t #se concidera analizado y corrupto todo el paquete la proxima se empieza desde cero
                break
            if (not reduce(lambda x,y: x^y, data[init_trama:init_trama+ COMM['L_FRAME']])): #esto es cualca, solo para reemplarzar el xor
                #parsea:
                self.data.channels[:,self.tramas_parseadas]=data[init_trama+COMM['CHANNELS_POS']:init_trama+COMM['CHANNELS_POS']+CONFIG['CANT_CANALES']]
                #ojo aca se tendria q parsear y guardar el resto de la informacion q viene en la trama                
                self.tramas_parseadas+=1
                contador_old=self.contador
                self.contador=data[init_trama+COMM['COUNTER_POS']]
                #comparo contadores aviso
                if np.int16(contador_old+1) != self.contador:
                    #guardo discontinuidad!!!
                    #print "perdida de datos segun contador"
                    logging.error(Errors_Messages[COUNTER_ERROR])
                    try:
                        self.send_warnings.put_nowait([COUNTER_ERROR,1])
                    except:
                        logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                    
                    
                #fin del parseo
  
            else:
                #print "dato erroneo detectado"
                logging.error(Errors_Messages[DATA_CORRUPTION])
                try:
                    self.send_warnings.put_nowait([DATA_CORRUPTION,1])
                except:
                    logging.error(Errors_Messages[SLOW_GRAPHICS_SIGNAL])
                #ckea, elimina dato, avisar corte y error de transmision
            self.c_t+=1
            
        
        if self.tramas_parseadas == CONFIG['PAQ_USB']:
            self.tramas_parseadas=0
            #retorno cuanto falta parsear del bloque crudo
            if self.c_t == max_c_t:
                self.c_t=0 
                return 0
            else:
                #me sobra data puedo volver a update
                return -1

        else:
            #retorno cuanto le falta para terminar el bloque de canales
            self.c_t=0
            return CONFIG['PAQ_USB'] - self.tramas_parseadas
    
    
