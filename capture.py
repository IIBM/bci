from multiprocessing import Process, Pipe,Array
import numpy as np #vectores, operaciones matematicas
import time #hora local 
import usb.core
import usb.util
import config
import os 
import array
from pyqtgraph.Qt import QtGui


intanVendor = 0x1CBE
intanProduct = 0x0003


def connect(idV,idP):
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
   


def parser(data,lectura):
    cadena=lectura[:config.LARGO_TRAMA*config.PAQ_USB].tostring()
    for i in range(0,config.PAQ_USB):
        data[:,i]=struct.unpack('<'+str(config.CANT_CANALES)+'H',cadena[i*config.LARGO_TRAMA+1:(i+1)*config.LARGO_TRAMA-1]) 
        if lectura[i*config.LARGO_TRAMA]!=255 or lectura[(i+1)*config.LARGO_TRAMA-1]!=70:
            print  "paquete roto"
        #con respecto al timestamp, puede tomarse como un dato mas, no deberia modificar nada
        #valores[:,i]=struct.unpack('>32h',data[5+i*LARGO_TRAMA:69+i*LARGO_TRAMA].tostring())


    
def obtener_datos(com,buffer_in,dev_usb,shared_mem):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    paq_data=config.LARGO_TRAMA*config.PAQ_USB
    dev_usb.write(1,'\xAA',0,100)
    save_data=False
    data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando='normal'

    while(comando != 'salir'):
        t1 = time.time()
        lectura = dev_usb.read(0x81,paq_data,0,400)                
        while not com.poll(): #mientras no se recivan comandos leo
            #tomar muchas muestras concatenerlas verificarlas y luego enviar y guardar
            #lectura = dev_usb.read(0x81,paq_data,0,200)
            
            while len(lectura) < paq_data:
                #config.LARGO_TRAMA*2**(n.bit_length() - 1)
                lectura.extend(dev_usb.read(0x81,paq_data,0,10))
             
            
            #parser(data,lectura) #castear todo junto es ligeramente mas rapido
            t1 = time.time()
            
            #buffer_in.send()
            shared_mem=lectura[:paq_data]
            print time.time()-t1 
            lectura=lectura[paq_data:]
            
            
            if save_data:
                pass
        comando=com.recv()
        save_data= comando=='guardar'
    dev_usb.write(1,'\xBB',0,100)


        
        
def capture_init():
        lectura_nueva = Array('B',config.PAQ_USB*config.LARGO_TRAMA)

        #verifica usb, luego comienza captura si es correcto
        if hasattr(config, 'FAKE_FILE'):
            reg_files=file_handle()
            datos_mostrar, datos_entrada = Pipe(duplex = False)
            control_usb, control_ui = Pipe(duplex = False)
            p_ob_datos = Process(target=fake_file_obtener_datos, args=(control_usb,datos_entrada,reg_files))
            return p_ob_datos,control_ui,datos_mostrar 
        
        #experim
        if hasattr(config, 'FAKE'):
            reg_files=file_handle()
            datos_mostrar, datos_entrada = Pipe(duplex = False)
            control_usb, control_ui = Pipe(duplex = False)
            p_ob_datos = Process(target=fake_obtener_datos, args=(control_usb,datos_entrada,reg_files,lectura_nueva))
            return p_ob_datos,control_ui,datos_mostrar,lectura_nueva      
        
   
                 
        dev_usb = connect(intanVendor,intanProduct)
        datos_mostrar, datos_entrada = Pipe(duplex = False)
        control_usb, control_ui = Pipe(duplex = False)
        p_ob_datos = Process(target=obtener_datos, args=(control_usb,datos_entrada,dev_usb,lectura_nueva))
        
        return p_ob_datos,control_ui,datos_mostrar

def fake_obtener_datos(com,buffer_in,reg_files,lectura_nueva):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    save_data=False
    comando='normal'
    while(comando != 'salir'):    
        while not com.poll():           
            lectura=array.array('B')
            while len(lectura) < (config.LARGO_TRAMA*config.PAQ_USB):
                lectura.append(205)
            
            #t1 = time.time()
                
            lectura_nueva=lectura
            #print time.time()-t1 
            if save_data:
                reg_files.save(data) 
            #agrega el largo del archivo
        comando=com.recv()
        save_data= comando=='guardar'   
    filereg_files.close()   

def fake_file_obtener_datos(com,buffer_in):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    file_input=open('data_test','rb')
    save_data=False
    data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando='normal'
    while(comando != 'salir'):
        if save_data:
            file_name = time.asctime( time.localtime(time.time())) 
            file=open(file_name,'wb')
            l_file=0;       
        while not com.poll():
            j=0
            while(j<config.PAQ_USB):
                data[:,j]=np.fromfile(file_input,np.int16, config.CANT_CANALES)
                basura=np.fromfile(file_input,np.int16,1)
                j+=1
            buffer_in.send(data) #leer file-leer usb
            if save_data:
                l_file+=1
                data.tofile(file)
        if save_data:   
            file.close()
            os.rename(file_name,file_name+'_m'+str(l_file))
            #agrega el largo del archivo
        comando=com.recv()
        save_data= comando=='guardar'
    file_input.close()
    print "termina proceso secundario"

class file_handle():
    #def __init__(self):
        #self.generic_file_name = QtGui.QFileDialog.getSaveFileName()
        ##archivo cabecera
        #file_head=open(self.generic_file_name + '0','w')
        #file_head.write("FS,LARGO_TRAMA,FECHA,LARGO_ARCHIVO,ARCHIVOS\n")
        #self.paqxfile=config.MAX_SIZE_FILE/config.LARGO_TRAMA/config.PAQ_USB
        #self.part=1 #parte del registro todo corrido
        #self.file_part=open(self.generic_file_name + str(self.part),'wb')
        #self.paq_in_part=0

    def save(self,data):
        
        
        if(self.paq_in_part<self.paqxfile):
            data.tofile(self.file_part)
            self.paq_in_part+=1
        else:
            self.file_part.close()
            self.file_part=open(self.generic_file_name + str(self.part),'wb')
            data.tofile(self.file_part)
            self.part=1

    def close(self):
        self.file_part.close()
        file_head.write(str(config.FS) + ','+ str(config.LARGO_TRAMA)+','+str(time.asctime( time.localtime(time.time())))+','+str(self.paqxfile*config.PAQ_USB)+','+str(self.part)+'\n')
        file_head.close()
