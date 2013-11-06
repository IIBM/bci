#!/usr/bin/python

from pyqtgraph.Qt import QtGui, QtCore #interfaz en general
import pyqtgraph as pg #graficos
import time #hora local 
from PyQt4  import uic #leer archivo con user interface
import os #ayuda a lo anterior y renombra archivo para largo
from data_processing import bci_data_handler
from libgraf import tets_display,plus_display
import config

# archivos de conf grafica... basica sin pg
uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')

   
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.tet_plus_selec
        #diagolo q da mas info del canal
        #self.dialogo=Dialog_Tet()
        #matriz de graficos general
        self.matriz_tetrodos=tets_display(self.espacio_pg)
        
        for i in range((config.CANT_CANALES)/4):
            self.tet_plus_selec.addItem('T%s' % (i + 1))

        
        self.info_tetrodo=plus_display(self.plus_grid,self.plus_grid_fr,self.c_auto_umbral,self.c_manual_umbral)
        #self.matriz_tasas=rates_display(self.ecualizer_grid,self.dialogo)    
        
        #quedo sin conectar xq no ser estandar de la interfaz
        
        
        QtCore.QObject.connect(self.autoRange, QtCore.SIGNAL("clicked()"), self.set_autoRange)
        #QtCore.QObject.connect(self.bars_scale, QtCore.SIGNAL("valueChanged(int)"), self.matriz_tasas.change_scale)
        QtCore.QObject.connect(self.canal_selec, QtCore.SIGNAL("valueChanged(int)"), self.info_tetrodo.change_channel)  
        QtCore.QObject.connect(self.tet_plus_selec, QtCore.SIGNAL("currentIndexChanged(int)"), self.info_tetrodo.change_tet) 
        QtCore.QObject.connect(self.tet_plus_mode, QtCore.SIGNAL("currentIndexChanged(int)"), self.info_tetrodo.change_display_mode) 
        QtCore.QObject.connect(self.c_auto_umbral, QtCore.SIGNAL("stateChanged(int)"), self.info_tetrodo.change_tmode) 
        
        
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0) #si va demasiado lento deberia bajarse el tiempo
        self.data_handler=bci_data_handler()
        self.t1 = time.time()
    
    def update(self):
        
        self.data_handler.update()
        if not self.pausa.isChecked():
            self.update_graficos()
        self.status.setText('update: '+str(int((time.time() - self.t1)*1000)))
        self.t1 = time.time()
        
    def update_graficos(self):    
        #self.dialogo.update(self.data)
        #self.matriz_tasas.update(self.tasas_disparo)
        self.matriz_tetrodos.update(self.data_handler.graf_data)
        self.info_tetrodo.update(self.data_handler.graf_data)
    
    def on_actionDetener(self):
        #detiene el guardado de datos
        self.data_handler.stopsave()

    def on_actionComenzar(self):
        self.data_handler.save2disc()
        
    def on_actionSalir(self):
        self.timer.stop()
        self.data_handler.close()
        #self.dialogo.close()
        self.close()
       
    def on_actionNuevo(self):
        self.data_handler.restart()

        
    def set_autoRange(self):
        if self.autoRange.isChecked():
            self.matriz_tetrodos.setAutoRange(True)
        else:
            self.matriz_tetrodos.setAutoRange(False)
        
        
    #@QtCore.pyqtSlot()          
    #def on_s_canal1_valueChanged(self,int):
        #print str(self.s_canal1.value())





        
def main():
    app = QtGui.QApplication([])
    window=MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
