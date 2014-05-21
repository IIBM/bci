import numpy as np #vectores, operaciones matematicas
import time #hora local 
import config
#import os 
import array
#from pyqtgraph.Qt import QtGui
from multiprocess_config import *


# Trama 
# byte alto   byte bajo
# 0xFF        Nro de canales
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
    LARGO_TRAMA=40
    save_data=False
    reg_files=file_handle(generic_file,LARGO_TRAMA)
    
    data=np.ndarray(config.CANT_CANALES*config.PAQ_USB,np.int16) #deberia ser mas grande y mandar al okapy uno mas grande
    channels=np.ndarray([config.CANT_CANALES,config.PAQ_USB],np.int16)
    dev.start(int(config.FS))
    parser=Parser(LARGO_TRAMA,config.PAQ_USB)
    comando='normal'
    contador=0
    while(comando != EXIT_SIGNAL):
        while not com.poll(): #mientras no se recivan comandos leo
            if (dev.data_available() >= 1000000):
                # data es un array de numpy de uint16
                # n es un entero que tiene la cantidad de palabras de 16 bits transmitidas
                n = dev.read_data(data) #deberia ser N mas grande, si me faltan N tramas
                parser.get_ch(data,channels)
                #lectura[:,contador*CANT_TRAMA_FIJO:contador*CANT_TRAMA_FIJO+CANT_TRAMA_FIJO]=np.reshape(data,[LARGO_TRAMA,CANT_TRAMA_FIJO],'F')
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
                time.sleep(100/config.FS)
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
        
            
        
class data_in():
    def __init__(self):
        self.data_loss_cuts=list()
        self.spikes=list()
        self.channels=ndarray([config.CANT_CANALES,config.PAQ_USB],np.uint16)
        
        
class Parser():
    def __init__(self,LARGO_TRAMA,CANT_TRAMA,CANT_CANALES):     
        self.contador_old=0
        self.FFplus=np.fromstring('\x23''\xff',np.int16)
        self.LARGO_TRAMA=LARGO_TRAMA
        self.CANT_TRAMA=CANT_TRAMA
        self.CANT_CANALES=CANT_CANALES
        
    def get_ch(self,data,channels):
        sinc=0
        c_t=0
        #primero sincroniza
        while sinc < self.LARGO_TRAMA:
            if (data[sinc] == FFplus and data[self.LARGO_TRAMA+sinc] == FFplus): #la segunda deberia ser el hash
                channels[:,c_t]=data[c_t*40+4+sinc:c_t*40+39+sinc]
                contador_old=(data[c_t*40+1+sinc:c_t*40+2+sinc])
                break
            sinc+=1    

        c_t+=1
        
        while c_t < self.CANT_TRAMA:
        #data_raw[c_t*40+1+sinc
            if(data[c_t*40+sinc] != self.FFplus): #desincronizado
            #sinc=incronizar(c_t*40+sinc)# esto cambia c_t y s
                print "desincronizacion detectada"
                break
            if (True == True): #esto es cualca, solo para reemplarzar el xor
                channels[:,trama_parseada]=data[c_t*40+4+sinc:c_t*40+39+sinc]
                contador_old=contador
                contador=data[c_t*40+1+sinc]
                #comparo contadores aviso
                if np.int16(contador_old+1) != contador:
                    #guardo discontinuidad!!!
                    print "perdida de datos contador"
        
        #if(trama_parseada is CANT_TRAMA):
            ##envio a cola
            #trama_parseada=0
  
            else:
                print "dato erroneo detectado"
                #ckea, elimina dato, avisar corte y error de transmision
            c_t+=1
        
