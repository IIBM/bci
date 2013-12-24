import numpy as np #vectores, operaciones matematicas
import time #hora local 
import usb.core
import usb.util
import config
#import os 
import array
#from pyqtgraph.Qt import QtGui


intanVendor = 0x1CBE
intanProduct = 0x0003
BUFFER_PAQ_USB=1  #COLA

def connect(idV=intanVendor,idP=intanProduct):
    # find our device
    dev = usb.core.find(idVendor=idV, idProduct=idP)
    msg = ('Device idVendor = ' + str(hex(idV)) + ' and idProduct = ' + str(hex(idP)) + ' not found')
    # was it found?
    if dev is None:
        raise ValueError(msg)
    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    dev.set_configuration()
    return dev
   

def fake_obtener_datos(com,send_warnings,reg_files,cola,generic_file):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    
    save_data=False
    comando='normal'
    while(comando != 'salir'):    
        while not com.poll():           
            lectura=array.array('B')
            while len(lectura) < (config.LARGO_TRAMA*config.PAQ_USB):
                lectura.append(205)
            
            #t1 = time.time()
            try:
			#cola.put_nowait(np.fromfile(file_input,'B',config.PAQ_USB*config.LARGO_TRAMA))
			    cola.put(lectura,timeout=config.TIEMPO_DISPLAY/10)
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
    reg_files=file_handle(generic_file)
    file_input=open('data_test','rb')
    save_data=False
    #data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando=''
    #tiempo_espera=float(config.TIEMPO_DISPLAY)/50    
    while(comando != config.EXIT_SIGNAL):      
        while not com.poll():
            #j=0
            #lectura=array.array('B')
            #lectura.append(file_input.read(config.PAQ_USB*config.LARGO_TRAMA))
            #lectura=file_input.read(config.PAQ_USB*config.LARGO_TRAMA)
            #for s in range(len(lectura)):
			#	lectura_nueva[s]=ord(lectura[s])
            
            #lectura_nueva[:]=np.fromfile(file_input,'B',config.PAQ_USB*config.LARGO_TRAMA)
            lectura_nueva=np.fromfile(file_input,'B',config.PAQ_USB*config.LARGO_TRAMA)
            data=np.fromstring(lectura_nueva, dtype='<i2')
            try:
                #cola.put_nowait(np.fromfile(file_input,'B',config.PAQ_USB*config.LARGO_TRAMA))
                #t1 = time.time()
                cola.put_nowait(data.reshape([config.CANT_CANALES+1,config.PAQ_USB],order='F'))
                #print (time.time() - t1)*1000
            except:
                try:
                    send_warnings.put_nowait("Loss data in slow processing")
                except:
                    pass	
            time.sleep(config.TIEMPO_DISPLAY)
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
        save_data= reg_files.actions(comando)
    file_input.close()
     

def obtener_datos(com,send_warnings,dev_usb,reg_files,cola,generic_file):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    paq_data=config.LARGO_TRAMA*config.PAQ_USB
    dev_usb.write(1,'\xAA',0,100)
    save_data=False
    data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando='normal'

    while(comando != config.EXIT_SIGNAL):
        t1 = time.time()
        lectura = dev_usb.read(0x81,paq_data,0,400)                
        while not com.poll(): #mientras no se recivan comandos leo
            #tomar muchas muestras concatenerlas verificarlas y luego enviar y guardar
            #lectura = dev_usb.read(0x81,paq_data,0,200)
            
            while len(lectura) < paq_data:
                #config.LARGO_TRAMA*2**(n.bit_length() - 1)
                lectura.extend(dev_usb.read(0x81,paq_data,0,10))
             
            #parser(data,lectura) #castear todo junto es ligeramente mas rapido
            #t1 = time.time()
            #buffer_in.send()
            #shared_mem=lectura[:paq_data]
            
            try:
                cola.put(lectura[:paq_data],timeout=config.TIEMPO_DISPLAY/10)
            except:
                send_warnings.send('Datos no mostrados')

            if save_data:
                reg_files.save(lectura[:paq_data]) 
            lectura=lectura[paq_data:]    
        comando=com.recv()
        save_data= comando=='guardar'
    dev_usb.write(1,'\xBB',0,100)



class file_handle():
    def __init__(self,generic_file):
        self.generic_file_name = generic_file
        #archivo cabecera
        self.paqxfile=config.MAX_SIZE_FILE/config.LARGO_TRAMA/config.PAQ_USB
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
        if signal is config.START_SIGNAL:
            self.num_registro+=1
            self.new()

            return True
        
        return False
    def close(self):
        try:
            self.file_part.close()
            file_head.write(str(config.FS) + ','+ str(config.LARGO_TRAMA)+','+str(time.asctime( time.localtime(time.time())))+','+str(self.paqxfile*config.PAQ_USB)+','+str(self.part)+'\n')
            file_head.close()
        except:
            pass

