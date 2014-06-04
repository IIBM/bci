import numpy as np #vectores, operaciones matematicas
import time #hora local 
from configuration import general_config as config
#import os 
#import array
from multiprocess_config import *
from configuration import data_frame_config as comm
from configuration import file_config



def connect():
    import okapi
    # find our device
    dev = okapi.OpalKelly()
    dev.reset()
    return dev
   

def fake_file_obtener_datos(com,send_warnings,cola):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    LARGO_TRAMA=2*config.CANT_CANALES+2    
    reg_files=file_handle()
    file_input=open('data_test','rb')
    save_data=False
    data2=data_in()
    #data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando=''
    #tiempo_espera=float(config.TIEMPO_DISPLAY)/50    
    while(comando != EXIT_SIGNAL):      
        while not com.poll():
            #j=0
            #lectura=array.array('B')
            #lectura.append(file_input.read(config.PAQ_USB*LARGO_TRAMA))
            #lectura=file_input.read(config.PAQ_USB*LARGO_TRAMA)
            #for s in range(len(lectura)):
            #    lectura_nueva[s]=ord(lectura[s])
            
            #lectura_nueva[:]=np.fromfile(file_input,'B',config.PAQ_USB*LARGO_TRAMA)
            lectura_nueva=np.fromfile(file_input,'B',config.PAQ_USB*LARGO_TRAMA)
            data=np.fromstring(lectura_nueva, dtype='<i2')
            try:
                #cola.put_nowait(np.fromfile(file_input,'B',config.PAQ_USB*LARGO_TRAMA))
                #t1 = time.time()
                new_data=data.reshape([config.CANT_CANALES+1,config.PAQ_USB],order='F')
                data2.channels=new_data[:-1,:]
                cola.put_nowait(data2)
                #print (time.time() - t1)*1000
            except:
                try:
                    send_warnings.put_nowait(SLOW_PROCESS_SIGNAL)
                except:
                    pass    
            time.sleep(config.PAQ_USB*0.9/config.FS)
            #print "graphicar pierde datos :("
            #while(j<config.PAQ_USB):
                #data[:,j]=np.fromfile(file_input,np.int16, config.CANT_CANALES)
                #basura=np.fromfile(file_input,np.int16,1)
                #j+=1
            #buffer_in.send(data) #leer file-leer usb
            if save_data:
                reg_files.save(lectura_nueva)
            #agrega el largo del archivo
        comando=com.recv()
        reg_files.actions(comando)
        save_data= comando=='guardar'
    file_input.close()
     

def obtener_datos(com,send_warnings,dev,cola):#SINCRONIZAR!!!! BUSCAR FF Y ENGANCHARSE
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer     
    import logging
    
    
    
    save_data=False
    logging.basicConfig(filename='data_bci.log',level=logging.WARNING)
    reg_files=file_handle()
    parser=Parser(cola)
    comando='normal'
    extra_data=0
    data=np.ndarray(comm.L_TRAMA*config.PAQ_USB*2,np.int16) #es el doble de grande que el que sera utilizado normalmente
    dev.start(int(config.FS))

    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo
            if (dev.data_available() >= 1000000):
                # data es un array de numpy de uint16
                # n es un entero que tiene la cantidad de palabras de 16 bits transmitidas
                new_pack_data=(config.PAQ_USB+extra_data)*comm.L_TRAMA
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
                            pass
                    if extra_data < 0: #sobraban datos
                        extra_data=parser.update(data[:new_pack_data]) 
                    else:
                        break
            else :
                time.sleep(100/config.FS)
        comando=com.recv()
        save_data= (comando==START_SIGNAL)
	reg_files.actions(comando)
    dev.close();

class file_handle():
    def __init__(self):
        #archivo cabecera
        self.paqxfile=file_config.MAX_SIZE_FILE*2**20/comm.L_TRAMA/config.PAQ_USB/np.int16().nbytes
        
        self.num_registro=-1

    def new(self):
        self.part=1 #parte del registro todo corrido
        
        self.file_part=open(file_config.GENERIC_FILE +'-'+str(self.num_registro) +'-' +str(self.part),'wb')
        
        self.paq_in_part=0
        
    def save(self,data):
        
        if(self.paq_in_part<self.paqxfile):
            data.tofile(self.file_part)
            self.paq_in_part+=1
        else:
            self.file_part.close()
            self.part+=1
            self.file_part=open(file_config.GENERIC_FILE +'-'+str(self.num_registro) +'-' +str(self.part),'wb')
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
            newsection='GENERAL_CONFIGURATION'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'fs',int(config.FS))
            config_parser.set(newsection,'#channels',config.CANT_CANALES)
            
            newsection='DATA_FRAME'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'largo_trama',comm.L_TRAMA)
            config_parser.set(newsection,'channels_pos',comm.CHANNELS_POS)
            config_parser.set(newsection,'counter_pos',comm.COUNTER_POS)
            config_parser.set(newsection,'hash_pos',comm.HASH_POS)
            
            newsection='DATA_INFO'
            config_parser.add_section(newsection)
            config_parser.set(newsection,'#files',self.part)
            config_parser.set(newsection,'date',time.asctime( time.localtime(time.time())))
            file_head= open(file_config.GENERIC_FILE +'-'+str(self.num_registro) + '-0','w')
            config_parser.write(file_head)
            file_head.close()
            self.file_part.close()
            
        
class data_in():
    def __init__(self):
        self.data_loss_cuts=list()
        self.spikes=list()
        self.channels=np.ndarray([config.CANT_CANALES,config.PAQ_USB],np.int16)
        
        
class Parser():
    def __init__(self,send_warnings):     
        self.contador=0 #el contador de la trama
        self.FFplus=np.fromstring('\x23''\xff',np.int16)
        self.tramas_parseadas=0 #ubicacion en el bloque q se esta creando
        
        self.data=data_in()
        self.c_t=0#ubicacion en el bloque q se esta leyendo
        self.sinc=0
        self.first_read=True
        self.send_warnings=send_warnings
    def update(self,data):
        max_c_t=data.size/comm.L_TRAMA
        #si recien empieza con esos datos, primero sincroniza
        if self.c_t==0 :
            self.sinc=0
            while self.sinc < comm.L_TRAMA:
                if (data[self.sinc] == self.FFplus) and (not reduce(lambda x,y: x^y, data[init_trama:init_trama+ comm.L_TRAMA])): #falta un and con el hash
                    #parsea:
                    self.data.channels[:,self.c_t]=data[comm.CHANNELS_POS+self.sinc:self.sinc+comm.CHANNELS_POS+config.CANT_CANALES]
                    self.tramas_parseadas+=1
                    contador_old=self.contador
                    self.contador=(data[comm.COUNTER_POS+self.sinc])
                    if np.int16(contador_old+1) != self.contador and self.first_read:
                        self.first_read=False
                        #guardo discontinuidad!!!
                        #print "perdida de datos segun contador"
                        logging.error(Errors_Messages[COUNTER_ERROR])
                        try:
                            self.send_warnings.put_nowait([COUNTER_ERROR,1])
                        except:
                            pass
                    #fin del priner parseo
                    break
                self.sinc+=1
            if(self.sinc >0 ):
                max_c_t=max_c_t-1
            if (self.sinc == comm.L_TRAMA):
                #print "se recorrio una trama y nunca se sincronizo"
                logging.error(Errors_Messages[CANT_SYNCHRONIZE])
                try:
                    self.send_warnings.put_nowait([CANT_SYNCHRONIZE,config.PAQ_USB])
                except:
                    pass
                self.first_read=True
                
                self.c_t=max_c_t #se concidera analizado y corrupto todo el paquete la proxima se empieza desde cero
            else:
                self.c_t+=1
        #recorre hasta llenar tramas parseadas o parsear todo el bloque de datos crudos
        while self.tramas_parseadas < config.PAQ_USB and self.c_t < max_c_t:
            init_trama=self.c_t*comm.L_TRAMA+self.sinc
            if(data[init_trama] != self.FFplus): #desincronizado
            #sinc=incronizar(c_t*40+sinc)# esto cambia c_t y s
                #print "desincronizacion detectada"
                logging.error(Errors_Messages[DATA_NONSYNCHRONIZED])
                try:
                    self.send_warnings.put_nowait([DATA_NONSYNCHRONIZED,config.PAQ_USB-self.c_t])
                except:
                    pass
                self.first_read=True
                self.c_t=max_c_t #se concidera analizado y corrupto todo el paquete la proxima se empieza desde cero
                break
            if (not reduce(lambda x,y: x^y, data[init_trama:init_trama+ comm.L_TRAMA])): #esto es cualca, solo para reemplarzar el xor
                #parsea:
                self.data.channels[:,self.tramas_parseadas]=data[init_trama+comm.CHANNELS_POS:init_trama+comm.CHANNELS_POS+config.CANT_CANALES]
                #ojo aca se tendria q parsear y guardar el resto de la informacion q viene en la trama                
                self.tramas_parseadas+=1
                contador_old=self.contador
                self.contador=data[init_trama+comm.COUNTER_POS]
                #comparo contadores aviso
                if np.int16(contador_old+1) != self.contador:
                    #guardo discontinuidad!!!
                    #print "perdida de datos segun contador"
                    logging.error(Errors_Messages[COUNTER_ERROR])
                    try:
                        self.send_warnings.put_nowait([COUNTER_ERROR,1])
                    except:
                        pass
                    
                    
                #fin del parseo
  
            else:
                #print "dato erroneo detectado"
                logging.error(Errors_Messages[DATA_CORRUPTION])
                try:
                    self.send_warnings.put_nowait([DATA_CORRUPTION,1])
                except:
                    pass
                #ckea, elimina dato, avisar corte y error de transmision
            self.c_t+=1
            
        
        if self.tramas_parseadas == config.PAQ_USB:
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
            return config.PAQ_USB - self.tramas_parseadas
    
    
