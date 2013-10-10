from multiprocessing import Process, Pipe
import numpy as np #vectores, operaciones matematicas
import time #hora local 
import usb.core
import usb.util
import config
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
    
def parser(data,tramas_leidas,lectura):
    cadena=lectura.tostring() #consume mas memoria pero va ligeramente mas rapido asi
    for i in range(tramas_leidas,len(data)/config.LARGO_TRAMA):
        data[:,i]=struct.unpack('>'+str(config.CANT_CANALES)+'h',cadena) 
        #con respecto al timestamp, puede tomarse como un dato mas, no deberia modificar nada
        #valores[:,i]=struct.unpack('>32h',data[5+i*LARGO_TRAMA:69+i*LARGO_TRAMA].tostring())


    
def obtener_datos(com,buffer_in,dev_usb):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    save_data=False
    data=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando='normal'
    while(comando != 'salir'):
        if save_data:
            file_name = time.asctime( time.localtime(time.time())) 
            file=open(file_name,'wb')
            file.write('config.FS= ' + str(config.FS) + ', config.CANT_CANALES= ' + str(config.CANT_CANALES) +'\n')
            l_file=0;
        while not com.poll(): #mientras no se recivan comandos leo
            #tomar muchas muestras concatenerlas verificarlas y luego enviar y guardar
            tramas_leidas=0
            while tramas_leidas != PAQ_USB:
                lectura = dev_usb.read(0x81,LARGO_TRAMA*(PAQ_USB-tramas_leidas),0,100)                
                parser(data,tramas_leidas,lectura) #castear todo junto es ligeramente mas rapido
                tramas_leidas+=len(data)/LARGO_TRAMA

            buffer_in.send(data) #leer file-leer usb
            if save_data:
                l_file+=1
                data.tofile(file)
        if save_data:   #si se estaba guardando se cierra el archivo
            file.close()
            os.rename(file_name,file_name+'_m'+str(l_file))
            #agrega el largo del archivo
        comando=com.recv()
        save_data= comando=='nuevo'


        
        
def capture_init(fake=False):
        #verifica usb, luego comienza captura si es correcto
        if hasattr(config, 'FAKE_FILE'):
            datos_mostrar, datos_entrada = Pipe(duplex = False)
            control_usb, control_ui = Pipe(duplex = False)
            p_ob_datos = Process(target=fake_file_obtener_datos, args=(control_usb,datos_entrada))
            return p_ob_datos,control_ui,datos_mostrar 
        
        
        if hasattr(config, 'FAKE'):
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
    data=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
    comando='normal'
    while(comando != 'salir'):
        if save_data:
            file_name = time.asctime( time.localtime(time.time())) 
            file=open(file_name,'wb')
            l_file=0;       
        while not com.poll():
            i=0
            j=0
            while(j<config.PAQ_USB):
                i=0
                while(i<config.CANT_CANALES):
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

def fake_file_obtener_datos(com,buffer_in,dev_usb=None):
    #lee datos del USB los guarda en un archivo si lo hay, los ordena en un vector y lo envia por el buffer  
    file_input=open('data_test','rb')
    save_data=False
    data=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
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
        save_data= comando=='nuevo'
    file_input.close()
    print "termina proceso secundario"
