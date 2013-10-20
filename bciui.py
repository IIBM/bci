#!/usr/bin/python

from pyqtgraph.Qt import QtGui, QtCore #interfaz en general
import pyqtgraph as pg #graficos

import numpy as np #vectores, operaciones matematicas
import time #hora local 
from scipy import signal #proc de segnales
from PyQt4  import uic #leer archivo con user interface
import os #ayuda a lo anterior y renombra archivo para largo

from capture import capture_init
from libgraf import Dialog_Tet,tets_display,rates_display
import config
import struct


#Filtros: (revisar orden del filtro, tardan demasiado)

[b_spike,a_spike]=signal.iirfilter(4,[float(300*2)/config.FS, float(6000*2)/config.FS], rp=None, rs=None, btype='band', analog=False, ftype='butter',output='ba')


# archivos de conf grafica... basica sin pg
uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')

def parser(data,lectura):
    cadena=lectura.tostring()
    for i in range(0,config.PAQ_USB):
        data[:,i]=struct.unpack('<'+str(config.CANT_CANALES)+'H',cadena[i*config.LARGO_TRAMA+1:(i+1)*config.LARGO_TRAMA-1]) 
        #if lectura[i*config.LARGO_TRAMA]!=255 or lectura[(i+1)*config.LARGO_TRAMA-1]!=70:
        #    print  "paquete roto"        
        
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        
        #diagolo q da mas info del canal
        self.dialogo=Dialog_Tet()
        #matriz de graficos general
        self.matriz_tetrodos=tets_display(self.espacio_pg)
        self.matriz_tasas=rates_display(self.ecualizer_grid,self.dialogo)    
 
        #inicializo vector de muestras en cero
        self.data=np.uint16(np.zeros([config.CANT_CANALES,config.CANT_DISPLAY]))
        self.data_new=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))       
        self.tasas_spikes=np.zeros(config.CANT_CANALES)
        #quedo sin conectar xq no ser estandar de la interfaz
        QtCore.QObject.connect(self.autoRange, QtCore.SIGNAL("clicked()"), self.set_autoRange)
        QtCore.QObject.connect(self.bars_scale, QtCore.SIGNAL("valueChanged(int)"), self.matriz_tasas.change_scale)
        self.run()
        
        #preparo proceso de adquisicion de datos
    def run(self):      
        self.p_ob_datos,self.control_sampler,self.datos_in=capture_init()
        #try:
            
        #except:
            #print(" ERROR EN INICIO USB")
            #self.close()
        
        self.p_ob_datos.start()
            
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0) #esto deberia cambiarse con un boton, ojo q afecta largo de vectores

    def update(self):
        if(self.datos_in.poll()):
            t1 = time.time()
            lectura=self.datos_in.recv()
            #t1 = time.time()
            parser(self.data_new,lectura)
            #print str(time.time()-t1) +'parser'
            if not self.pausa.isChecked():
                
                #self.data=np.append(self.data[:,config.CANT_DISPLAY:],data_new,axis=1)
                self.data=np.concatenate([self.data[:,config.PAQ_USB:], self.data_new],axis=1) #hace lo mismo q la de arriba... no encontre mejoras
                self.tasas_disparo,umbrales=calcular_tasas_disparo(self.data) 
            self.update_graficos()
            self.status.setText('update: '+str(int((time.time() - t1)*1000)))
          
    def update_graficos(self):    
        self.dialogo.update(self.data)
        self.matriz_tasas.update(self.tasas_disparo)
 
        self.matriz_tetrodos.update(self.data)
        
    
    def on_actionDetener(self):
        #detiene el guardado de datos
        self.control_sampler.send('detener')

    def on_actionComenzar(self):
        self.control_sampler.send('guardar')
        
    def on_actionSalir(self):
        self.control_sampler.send('salir')
        self.p_ob_datos.join(1)
        self.dialogo.close()
        self.close()
    
    def on_actionNuevo(self):
        self.control_sampler.send('salir')
        self.p_ob_datos.join(1)
        self.run()
        
    def set_autoRange(self):
        if self.autoRange.isChecked():
            self.matriz_tetrodos.setAutoRange(True)
        else:
            self.matriz_tetrodos.setAutoRange(False)
        
        
    #@QtCore.pyqtSlot()          
    #def on_s_canal1_valueChanged(self,int):
        #print str(self.s_canal1.value())


def calcular_tasas_disparo(data):
    x=abs(signal.lfilter(b_spike,a_spike,data-np.mean(data,0)))
    umbrales=4*np.median(x/0.6745,1)
    tasas=np.zeros(config.CANT_CANALES)
    for i in range(config.CANT_CANALES):
        pasa_umbral=(x[i,:]>umbrales[i])
        tasas[i]=np.sum(pasa_umbral[:-1] * ~ pasa_umbral[1:])
    return tasas,umbrales


        
def main():
    app = QtGui.QApplication([])
    
    window=MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
