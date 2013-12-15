#!/usr/bin/python

from pyqtgraph.Qt import QtGui, QtCore #interfaz en general
#import pyqtgraph as pg #graficos
import time #hora local 
from PyQt4  import uic #leer archivo con user interface
import os #ayuda a lo anterior y renombra archivo para largo
from data_processing import bci_data_handler
from libgraf import plus_display,general_display
#import config

# archivos de conf grafica... basica sin pg
uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')

   
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        #self.tet_plus_selec
        #diagolo q da mas info del canal
        #self.dialogo=Dialog_Tet()
        #matriz de graficos general
        #self.matriz_tetrodos=tets_display(self.espacio_pg)
        #for i in range((config.CANT_CANALES)/4):
            #self.tet_plus_selec.addItem('T%s' % (i + 1))

        self.generic_file=QtGui.QFileDialog.getSaveFileName()

        self.info_tetrodo=plus_display(self.plus_grid,self.plus_grid_fr,self.c_auto_umbral,self.c_manual_umbral,self.beepbox)
        self.matriz_tetrodos=general_display(self.espacio_pg,self.info_tetrodo)

        #self.matriz_tasas=rates_display(self.ecualizer_grid,self.dialogo)    
        
        #quedo sin conectar xq no ser estandar de la interfaz
        
        
        #QtCore.QObject.connect(self.autoRange, QtCore.SIGNAL("clicked()"), self.set_autoRange)
        #QtCore.QObject.connect(self.bars_scale, QtCore.SIGNAL("valueChanged(int)"), self.matriz_tasas.change_scale)
        #QtCore.QObject.connect(self.tet_plus_selec, QtCore.SIGNAL("currentIndexChanged(int)"), self.info_tetrodo.change_tet) 
        QtCore.QObject.connect(self.tet_plus_mode, QtCore.SIGNAL("currentIndexChanged(int)"), self.info_tetrodo.change_display_mode) 
        QtCore.QObject.connect(self.c_auto_umbral, QtCore.SIGNAL("stateChanged(int)"), self.info_tetrodo.change_tmode) 
        QtCore.QObject.connect(self.escala_display, QtCore.SIGNAL("valueChanged(int)"), self.matriz_tetrodos.change_Yrange)  

        self.file_label.setText('Sin Guardar')
        self.contador_registro=-1
        self.timer = QtCore.QTimer()
        
        self.timer.timeout.connect(self.update)
        self.data_handler=bci_data_handler(self.generic_file)   
        #while(True):
            #try:
                     
                #break
            #except:
                #if(QtGui.QMessageBox.question(self, 'Error', "Dispositivo usb no detectado, volver a intentar?", 
                #QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.No ):
                    #exit()
            
        QtCore.QObject.connect(self.paq_view, QtCore.SIGNAL("valueChanged(int)"), self.changeXrange)  

        self.timer.start(0) #si va demasiado lento deberia bajarse el tiempo
        self.t1 = time.time()
        
    def update(self):
        
        status=self.data_handler.update()
        self.warnings.setText(status)
        if not self.pausa.isChecked():
            self.update_graficos()
        self.status.setText('update: '+str(int((time.time() - self.t1)*1000)))
        self.t1 = time.time()
        
    def update_graficos(self):    
        #self.dialogo.update(self.data)
        #self.matriz_tasas.update(self.tasas_disparo)
        self.matriz_tetrodos.update(self.data_handler.graf_data,self.data_handler.n_view,self.data_handler.xtime)
        info_selec=self.info_tetrodo.update(self.data_handler.graf_data,self.data_handler.data_new,self.data_handler.n_view,self.data_handler.xtime)
        self.info_label.setText('TET:'+str(info_selec[0]+1)+' C:'+str(info_selec[1]+1))
    
    def on_actionDetener(self):
        #detiene el guardado de datos
        self.data_handler.stopsave()
        self.file_label.setText('Sin Guardar')

    def on_actionSalir(self):
        self.timer.stop()
        self.data_handler.close()
        #self.dialogo.close()
        self.matriz_tetrodos.close()
        self.close()
       
    def on_actionNuevo(self):
        self.data_handler.startsave()
        self.contador_registro+=1
        self.file_label.setText('Guardando:'+self.generic_file +'-'+str(self.contador_registro))

    #def set_autoRange(self):
        #if self.autoRange.isChecked():
            #self.matriz_tetrodos.setAutoRange(True)
        #else:
            #self.matriz_tetrodos.setAutoRange(False)
        
    def closeEvent(self, event):
        self.on_actionSalir()
        
    def changeXrange(self,i):
        self.data_handler.change_paq_view(i)
        self.matriz_tetrodos.changeXrange(i)
        
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
