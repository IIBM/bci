#!/usr/bin/python

from pyqtgraph.Qt import QtGui, QtCore #interfaz en general
import pyqtgraph as pg #graficos

import numpy as np #vectores, operaciones matematicas
import time #hora local 
from scipy import signal #proc de segnales
from PyQt4  import uic #leer archivo con user interface
import os #ayuda a lo anterior y renombra archivo para largo

from capture import capture_init
from libgraf import bar_graf,Dialog_Tet,tets_display
from config import *



#Filtros: (revisar orden del filtro, tardan demasiado)

[b_spike,a_spike]=signal.iirfilter(4,[float(300*2)/FS, float(6000*2)/FS], rp=None, rs=None, btype='band', analog=False, ftype='butter',output='ba')


# archivos de conf grafica... basica sin pg
uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')

        
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        
        #matriz de graficos general
        self.matriz_tetrodos=tets_display(self.espacio_pg)
               
        #diagolo q da mas info del canal
        self.dialogo=Dialog_Tet()
        
        
        layout_ecualizer= pg.GraphicsLayout() #para ordenar los graficos(items) asi como el simil con los widgets
        self.ecualizer_grid.setCentralItem(layout_ecualizer)
        self.tasa_bars=list()
        for i in range((CANT_CANALES)/4):
            graf=bar_graf(i,self.tasa_bars,self.dialogo)
            layout_ecualizer.addItem(graf,row=None, col=None, rowspan=1, colspan=1)
                

        
        #inicializo vector de muestras en cero
        self.data=np.int16(np.zeros([CANT_CANALES,CANT_DISPLAY]))        
        self.tasas_spikes=np.zeros(CANT_CANALES)
        #quedo sin conectar xq no ser estandar de la interfaz
        QtCore.QObject.connect(self.autoRange, QtCore.SIGNAL("clicked()"), self.set_autoRange)
        
        
        #preparo proceso de adquisicion de datos
        try:
            self.p_ob_datos,self.control_sampler,self.datos_in=capture_init(fake=True)
        except:
            print(" ERROR EN INICIO USB")
            self.on_actionSalir()
        
        self.p_ob_datos.start()
            
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(TIEMPO_DISPLAY) #esto deberia cambiarse con un boton, ojo q afecta largo de vectores

    def update(self):
        if(self.datos_in.poll()):
            t1 = time.time()

            if not self.pausa.isChecked():
                data_new=self.datos_in.recv() 
                self.data=np.concatenate((self.data[:,CANT_DISPLAY:], data_new),axis=1) 
                self.tasas_spikes=calcular_tasas_spikes(self.data) 
            self.update_graficos()
            self.status.setText('update: '+str(int((time.time() - t1)*1000)))
          
    def update_graficos(self):    

        self.dialogo.update(self.data)
        
        for i in range(len(self.tasa_bars)):
            self.tasa_bars[i].setData(x=[i-0.3,i+0.3],y=[self.tasas_spikes[i],self.tasas_spikes[i]], _callSync='off')
        
        self.matriz_tetrodos.update(self.data)
        


    
    def on_actionDetener(self):
        #detiene el guardado de datos
        self.control_sampler.send('detener')
    
    def on_actionNuevo(self):
        #Comienza el guardado de datos, abre el archivo etc
        self.control_sampler.send('nuevo')
       

    def on_actionSalir(self):
        self.control_sampler.send('salir')
        self.p_ob_datos.join(1)
        self.dialogo.close()
        self.close()
    
    def set_autoRange(self):
        if self.autoRange.isChecked():
            self.matriz_tetrodos.setAutoRange(True)
        else:
            self.matriz_tetrodos.setAutoRange(False)
        
        
    #@QtCore.pyqtSlot()          
    #def on_s_canal1_valueChanged(self,int):
        #print str(self.s_canal1.value())



def calcular_tasas_spikes(data):
    umbrales=4*np.median(abs(signal.lfilter(b_spike,a_spike,data))/0.6745,1)
    return np.random.random(np.size(data,0))*100


        
def main():
    app = QtGui.QApplication([])
    
    window=MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
