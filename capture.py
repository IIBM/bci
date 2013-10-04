from multiprocessing import Process, Pipe
import numpy as np #vectores, operaciones matematicas
import time #hora local 
import usb.core
import usb.util
from config import *
import os 


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
    
    
def obtener_datos(com,buffer_in,dev_usb=None):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    save_data=False
    data=np.int16(np.zeros([CANT_CANALES,PAQ_USB]))
    comando='normal'
    while(comando != 'salir'):
        if save_data:
            file_name = time.asctime( time.localtime(time.time())) 
            file=open(file_name,'wb')
            l_file=0;       
        while not com.poll():
            #tomar muchas muestras concatenerlas verificarlas y luego enviar y guardar
            j=0
            while(j<PAQ_USB):
                ret = dev.read(0x81,(70)*100,0,100)
                #aca hay q parsear...
                for i in range(100):
                    data[i,:]=0 #una columna ya parseada
                j+=100
            buffer_in.send(data) #leer file-leer usb
            if save_data:
                l_file+=1
                data.tofile(file)
        if save_data:   
            file.close()
            os.rename(file_name,file_name+'_m'+str(l_file))
            #agrega el largo del archivo
        comando=com.recv()
        save_data= comando=='nuevo'

        
        
def capture_init(fake=False):
        #verifica usb, luego comienza captura si es correcto
        
        if fake:
            datos_mostrar, datos_entrada = Pipe(duplex = False)
            control_usb, control_ui = Pipe(duplex = False)
            p_ob_datos = Process(target=fake_obtener_datos, args=(control_usb,datos_entrada))
            return p_ob_datos,control_ui,datos_mostrar      
        
                 
        dev_usb = connect(intanVendor,intanProduct)
        dev_usb.write(1,'\xAA',0,100)
        
        datos_mostrar, datos_entrada = Pipe(duplex = False)
        control_usb, control_ui = Pipe(duplex = False)
        p_ob_datos = Process(target=obtener_datos, args=(control_usb,datos_entrada,dev_usb))
        
        return p_ob_datos,control_ui,datos_mostrar

def fake_obtener_datos(com,buffer_in,dev_usb=None):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    save_data=False
    data=np.int16(np.zeros([CANT_CANALES,PAQ_USB]))
    comando='normal'
    while(comando != 'salir'):
        if save_data:
            file_name = time.asctime( time.localtime(time.time())) 
            file=open(file_name,'wb')
            l_file=0;       
        while not com.poll():
            i=0
            j=0
            while(j<PAQ_USB):
                i=0
                while(i<CANT_CANALES):
                    new=(np.random.random()-0.5)*100
                    while(new is 0):
                        new=(np.random.random()-j*i)*100
                    data[i,j]=new
                    i+=1
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
        save_data= comando=='nuevo'
