#!/usr/bin/python

import config
import struct
import array
from scipy import signal #proc de segnales
from capture import capture_init
import numpy as np #vectores, operaciones matematicas


[b_spike,a_spike]=signal.iirfilter(4,[float(300*2)/config.FS, float(6000*2)/config.FS], rp=None, rs=None, btype='band', analog=False, ftype='butter',output='ba')



class  bci_data_handler():
    def __init__(self):
       
        #ojo aca!!!!1
        #self.graf_data=np.uint16(np.zeros([config.CANT_CANALES,config.CANT_DISPLAY]))
        #self.graf_data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB])) 
        self.graf_data=np.int16(np.zeros([config.CANT_CANALES,config.CANT_DISPLAY]))
        self.data_new=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB])) 
        #self.aux=array.array('B',[0 for i in range(config.PAQ_USB*config.LARGO_TRAMA)])
        self.paqdisplay=0
        self.p_ob_datos,self.control_subproc,self.warnigns_subproc,self.cola=capture_init()
        self.p_ob_datos.start()
        #try:
            
        #except:
            #print(" ERROR EN INICIO USB")
            #self.close()
        
    def update(self):
        aux=array.array('B')
        aux.extend(self.cola.get())
        
        for i in range(0,config.PAQ_USB):
            #ojo aca!!!!!!!!!
            #data[:,i]=struct.unpack('<'+str(config.CANT_CANALES)+'H',cadena[i*config.LARGO_TRAMA+1:(i+1)*config.LARGO_TRAMA-1]) 
            self.data_new[:,i]=struct.unpack('<'+str(config.CANT_CANALES)+'h',aux[i*config.LARGO_TRAMA:(i+1)*config.LARGO_TRAMA]) 
            #if lectura[i*config.LARGO_TRAMA]!=255 or lectura[(i+1)*config.LARGO_TRAMA-1]!=70:
        
        #self.data=np.append(self.data[:,config.CANT_DISPLAY:],data_new,axis=1)
        #self.graf_data=np.concatenate([self.graf_data[:,config.PAQ_USB:], self.data_new],axis=1) #hace lo mismo q la de arriba... no encontre mejoras
        self.graf_data[:,self.paqdisplay*config.PAQ_USB:(self.paqdisplay+1)*config.PAQ_USB]=self.data_new
        self.paqdisplay+=1
        if self.paqdisplay is config.PAQ_DISPLAY:
            self.paqdisplay=0
        if (not self.warnigns_subproc.empty() and self.warnigns_subproc.get()):
            print "se pierden datos"
    def stopsave(self):
        #detiene el guardado de datos
        self.control_subproc.send('detener')

    def save2disc(self):
        self.control_subproc.send('guardar')        #    print  "paquete roto"        
    
    def close(self):
        self.control_subproc.send('salir')
        self.p_ob_datos.join(1)
        self.p_ob_datos.terminate()
        #self.cola.close()
        
    def restart(self):
    
        self.control_subproc.send('restart') 
        
def calcular_umbral_disparo(data,canales):
    x=abs(signal.lfilter(b_spike,a_spike,data[canales,:]-np.mean(data[canales,:],0)))
    umbrales=4*np.median(x/0.6745,1)
    return x,umbrales
    

def calcular_tasa_disparo(x,umbral):
    pasa_umbral=(x>umbral)
    return np.sum(pasa_umbral[:-1] * ~ pasa_umbral[1:])
