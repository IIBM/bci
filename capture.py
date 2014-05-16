import numpy as np #vectores, operaciones matematicas
import time #hora local 
import config
#import os 
import array
#from pyqtgraph.Qt import QtGui
from multiprocess_config import *


# Trama 
# byte alto   byte bajo
#      0xFF   Nro de canales
# H_contador  L_contador
# config      config
# config      config
# C0_H        C0_L
# ...         ...
# C31_H       C31_L 
# AUX1_H      AUX1_L
# AUX2_H      AUX2_L
# VCC_H       VCC_L
# CRC_H       CRC_L




def connect():
    import okapi
    # find our device
    dev = okapi.OpalKelly()
    dev.reset()
    return dev
   

def fake_obtener_datos(com,send_warnings,reg_files,cola,generic_file):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    
    save_data=False
    comando='normal'
    while(comando != 'salir'):    
        while not com.poll():           
            lectura=array.array('B')
            while len(lectura) < (LARGO_TRAMA*config.PAQ_USB):
                lectura.append(205)
            
            #t1 = time.time()
            try:
            #cola.put_nowait(np.fromfile(file_input,'B',config.PAQ_USB*LARGO_TRAMA))
                cola.put(lectura,timeout=TIMEOUT_PUT)
            except:
                send_warnings.send('Datos no mostrados')
            #lectura_nueva=lectura
            #print time.time()-t1 
            if save_data:
                reg_files.save(lectura) 
            #agrega el largo del archivo
        comando=com.recv()
        save_data= comando=='guardar'   
    filereg_files.close()   

def fake_file_obtener_datos(com,send_warnings,cola,generic_file):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    LARGO_TRAMA=2*config.CANT_CANALES+2    
    reg_files=file_handle(generic_file,LARGO_TRAMA)
    file_input=open('data_test','rb')
    save_data=False
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
                cola.put_nowait(new_data[:-1,:])
                #print (time.time() - t1)*1000
            except:
                try:
                    send_warnings.put_nowait(SLOW_PROCESS_SIGNAL)
                except:
                    pass    
            time.sleep(config.PAQ_USB/config.FS)
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
     

def obtener_datos(com,send_warnings,dev,cola,generic_file):#SINCRONIZAR!!!! BUSCAR FF Y ENGANCHARSE
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    LARGO_TRAMA=config.CANT_CANALES
    CANT_TRAMA_FIJO=25
    pedidos=config.PAQ_USB/CANT_TRAMA_FIJO
    paq_data=LARGO_TRAMA*CANT_TRAMA_FIJO
    save_data=False
    reg_files=file_handle(generic_file,LARGO_TRAMA)
    lectura=np.ndarray([config.CANT_CANALES,config.PAQ_USB],np.uint16)
    dev.start()
    comando='normal'
    contador=0
    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo
            if (dev.is_data_ready() == True):
                # data es un array de numpy de uint16
                # n es un entero que tiene la cantidad de palabras de 16 bits transmitidas
                data,n = dev.read_data(paq_data) 
                lectura[:,contador*CANT_TRAMA_FIJO:contador*CANT_TRAMA_FIJO+CANT_TRAMA_FIJO]=np.reshape(np.fromstring(data,np.uint16),[LARGO_TRAMA,CANT_TRAMA_FIJO],'F')
                contador+=1
                if contador == pedidos:

                    contador=0
                    try:
                        cola.put(lectura,timeout=TIMEOUT_PUT)

                    except:
                        try:
                            send_warnings.put_nowait(SLOW_PROCESS_SIGNAL)
                        except:
                            pass
                
                    if save_data:
                        reg_files.save(lectura) 

                else :
                    time.sleep(2/config.FS)
        comando=com.recv()
        save_data= (comando==START_SIGNAL)
	reg_files.actions(comando)
    dev.close();

class file_handle():
    def __init__(self,generic_file,LARGO_TRAMA):
        self.generic_file_name = generic_file
        #archivo cabecera
        self.paqxfile=config.MAX_SIZE_FILE/LARGO_TRAMA/config.PAQ_USB
        self.num_registro=-1
        
    def new(self):
	file_head=open(self.generic_file_name +'-'+str(self.num_registro) + '-0','w')
        file_head.write("FS,LARGO_TRAMA,FECHA,LARGO_ARCHIVO,ARCHIVOS\n")
        self.part=1 #parte del registro todo corrido
        self.file_part=open(self.generic_file_name +'-'+str(self.num_registro) +'-' +str(self.part),'wb')
        self.paq_in_part=0
        
    def save(self,data):
        
        if(self.paq_in_part<self.paqxfile):
            data.tofile(self.file_part)
            self.paq_in_part+=1
        else:
            self.file_part.close()
            self.file_part=open(self.generic_file_name +'-'+str(self.num_registro) +'-' +str(self.part),'wb')
            data.tofile(self.file_part)
            self.part=1
    
    def actions(self,signal):
        self.close()
        if signal is START_SIGNAL:
            self.num_registro+=1
            self.new()
	elif signal is EXIT_SIGNAL:
            self.close()

    def close(self):
        try:
            self.file_part.close()
            file_head.write(str(config.FS) + ','+ str(LARGO_TRAMA)+','+str(time.asctime( time.localtime(time.time())))+','+str(self.paqxfile*config.PAQ_USB)+','+str(self.part)+'\n')
            file_head.close()
        except:
            pass
        
        
class data_in_parser():
    def __init__(self):
        self.data=data_in()
        self.c=np.int()
        self.desynchronized_flag=False
        
        
class data_in():
    def __init__(self):
        self.data_loss_cuts=list()
        self.spikes=list()
        self.channels=ndarray([config.CANT_CANALES,config.PAQ_USB],np.uint16)
