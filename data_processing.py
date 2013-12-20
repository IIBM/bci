#!/usr/bin/python

import config
import struct
import array
from scipy import signal #proc de segnales
from capture import capture_init
import numpy as np #vectores, operaciones matematicas
import time
from multiprocessing import Process, Pipe,Queue
[b_spike,a_spike]=signal.iirfilter(4,[float(300*2)/config.FS, float(6000*2)/config.FS], rp=None, rs=None, btype='band', analog=False, ftype='butter',output='ba')

MEAN_L=5  #ESTO PODRIA PONERSE A BASE DE TIEMPO


class  bci_data_handler():
    def __init__(self,generic_file):
       
        #ojo aca!!!!1
        #self.graf_data=np.uint16(np.zeros([config.CANT_CANALES,config.CANT_DISPLAY]))
        #self.graf_data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB])) 
        self.data_new=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB])) 
        #self.aux=array.array('B',[0 for i in range(config.PAQ_USB*config.LARGO_TRAMA)])
        self.graf_data=np.int16(np.zeros([config.CANT_CANALES,config.MAX_PAQ_DISPLAY*config.PAQ_USB]))
        self.p_ob_datos,self.control_subproc,self.warnigns_subproc,self.cola=capture_init(generic_file)
        self.mean_calc=np.int16(np.zeros([config.CANT_CANALES,MEAN_L]))
        self.paqdisplay=0
        self.mean_l=0
        self.paq_view=1
        self.new_paq_view=1
        self.n_view=self.paq_view*config.PAQ_USB
        self.xtime=np.zeros([config.MAX_PAQ_DISPLAY*config.PAQ_USB])
        self.xtime[:self.n_view]=np.linspace(0,config.MAX_PAQ_DISPLAY*config.PAQ_USB/float(config.FS),self.n_view)
        self.p_ob_datos.start()
        self.update()
        self.binary_data=array.array('B')
        self.binary_data.extend(self.cola.get())
        ####
    
    def update(self):
        #aux=array.array('B')
        #self.binary_data=self.cola.get()
        
        
        data_fake=np.int16(np.zeros([config.CANT_CANALES+1,config.PAQ_USB]))
        #aux.extend(self.cola.get())        
        t1=time.time()
        #for i in range(0,config.PAQ_USB):
            ##ojo aca!!!!!!!!!
            ##data[:,i]=struct.unpack('<'+str(config.CANT_CANALES)+'H',cadena[i*config.LARGO_TRAMA+1:(i+1)*config.LARGO_TRAMA-1]) 
            ##data_fake[:,i]=struct.unpack('<'+str(config.CANT_CANALES+1)+'h',self.binary_data[i*config.LARGO_TRAMA:(i+1)*config.LARGO_TRAMA]) 
            #data_fake[:,i]=struct.unpack_from('<'+str(config.CANT_CANALES+1)+'h',self.binary_data,i*config.LARGO_TRAMA)
            ###if lectura[i*config.LARGO_TRAMA]!=255 or lectura[(i+1)*config.LARGO_TRAMA-1]!=70:
        data_fake=np.fromstring(self.cola.get(), dtype='<i2')
        data_fake=data_fake.reshape([config.CANT_CANALES+1,config.PAQ_USB],order='F')
        
        print (time.time()-t1)*1000
        self.data_new=data_fake[:-1,:]
        
        
        
        #self.data=np.append(self.data[:,config.CANT_DISPLAY:],data_new,axis=1)
        #self.graf_data=np.concatenate([self.graf_data[:,config.PAQ_USB:], self.data_new],axis=1) #hace lo mismo q la de arriba... no encontre mejoras
        self.mean_calc[:,self.mean_l]=np.mean(self.data_new,1)
        self.mean_l+=1
        if self.mean_l is MEAN_L :
            self.mean_l=0
            
        
        mean_aux=np.mean(self.mean_calc,1)
        if(self.new_paq_view != self.paq_view):
            self.paq_view=self.new_paq_view
            self.n_view=self.paq_view*config.PAQ_USB
            self.xtime[:self.n_view]=np.linspace(0,self.n_view/float(config.FS),self.n_view)
        
        if self.paqdisplay >= self.paq_view:
            self.paqdisplay=0
            

        
        for i in range(config.PAQ_USB):
            self.graf_data[:,self.paqdisplay*config.PAQ_USB+i]=self.data_new[:,i]-mean_aux
        self.paqdisplay+=1
        
            
        if (not self.warnigns_subproc.empty()):
            return self.warnigns_subproc.get()
        else:
            return ''
            
    def stopsave(self):
        #detiene el guardado de datos
        self.control_subproc.send(config.STOP_SIGNAL)
    
    def close(self):
        self.control_subproc.send(config.EXIT_SIGNAL)
        self.p_ob_datos.join(1)
        self.p_ob_datos.terminate()
        #self.cola.close()
        
    def startsave(self):
        self.control_subproc.send(config.START_SIGNAL) 

    def change_paq_view(self,i):
        self.new_paq_view=i
    
        
        
def calcular_umbral_disparo(data,canales):
    x=abs(signal.lfilter(b_spike,a_spike,data[canales,:]))
    umbrales=4*np.median(x/0.6745,1)
    return x,umbrales
    

def calcular_tasa_disparo(x,umbral):
    if umbral >= 0:
        pasa_umbral=(x>umbral)
    else:
        pasa_umbral=(x<umbral)
    return np.sum(pasa_umbral[:-1] * ~ pasa_umbral[1:])


#def processing_init():
    #cola = Queue(maxsize=BUFFER_PAQ_USB)
    #control_prossesing, control_ui = Pipe(duplex = False)
    #p_ob_datos = Process(target=procesar_datos, args=(control,cola_data,cola_graf))
    #return p_ob_datos,control_ui,cola  

def data_processing(control,cola_input ,cola_graf):
        mean_calc=np.int16(np.zeros([config.CANT_CANALES,MEAN_L]))
        binary_data=array.array('B')
        binary_data.extend(cola_input.get())
        tasas=np.zeros([config.CANT_CANALES])
        comando=''
        
        ## FAKE
        data_fake=np.int16(np.zeros([config.CANT_CANALES+1,config.PAQ_USB]))
        while(comando != config.EXIT_SIGNAL):
            while not control.poll():
                self.binary_data=self.cola.get()
                
                for i in range(0,config.PAQ_USB):
                #ojo aca!!!!!!!!!
                #data[:,i]=struct.unpack('<'+str(config.CANT_CANALES)+'H',cadena[i*config.LARGO_TRAMA+1:(i+1)*config.LARGO_TRAMA-1]) 
                    data_fake[:,i]=struct.unpack_from('<'+str(config.CANT_CANALES+1)+'h',self.binary_data,i*config.LARGO_TRAMA)
                self.data_new=data_fake[:-1,:] #FAKE OJO ACA
        
            #procesoosososososos
            self.mean_calc[:,self.mean_l]=np.mean(self.data_new,1)
            self.mean_l+=1
            if self.mean_l is MEAN_L:
                self.mean_l=0
            for i in range(config.PAQ_USB):
                data[:,self.paqdisplay*config.PAQ_USB+i]=self.data_new[:,i]-mean_aux

            comando=control.recv()

class  procces_control_class():  
    def __init__(self):             
        self.umbrales=np.int16(np.zeros([config.CANT_CANALES]))
        self.filter_data=False
        
class  graff_data_class():   
     def __init__(self):     
        self.data_new=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
        self.tasas=np.zeros(config.CANT_CANALES)
        self.spikes_times=0
