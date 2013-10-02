from pyqtgraph.Qt import QtGui, QtCore #interfaz en general
import pyqtgraph as pg #graficos
import os
from PyQt4  import uic

uifile_menu = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'menu.ui') 

uifile_dialog = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'tet_dialog.ui')

class  bar_graf(pg.PlotItem):
    def __init__(self,i,tasa_bars,dialogo):
        vb=ViewBox_Bars(i,dialogo)
        pg.PlotItem.__init__(self,viewBox=vb,title="Tet."+str(i+1))
        self.showAxis('bottom', False)
        self.setMenuEnabled(enableMenu=False)
        self.showAxis('left', False)
        self.enableAutoRange('y', False)
        self.setYRange(0, 100)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()
        tasa_bars.append(self.plot(pen='r', fillLevel=0,brush=pg.mkBrush('r')))
        tasa_bars.append(self.plot(pen='y', fillLevel=0,brush=pg.mkBrush('y')))
        tasa_bars.append(self.plot(pen='g', fillLevel=0,brush=pg.mkBrush('g')))
        tasa_bars.append(self.plot(pen='c', fillLevel=0,brush=pg.mkBrush('c')))     
        
class ViewBox_Bars(pg.ViewBox):
    def __init__(self,i,dialogo):
        pg.ViewBox.__init__(self)
        self.canal=i
        self.dialogo=dialogo
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dialogo.show()
            self.dialogo.tet_selec=self.canal

class Dialog_Tet(QtGui.QDialog):
    #Ventana extra que se abre al clickear las barras        
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi(uifile_dialog,self)
        self.pg_widget.setMenuEnabled(enableMenu=False,enableViewBoxMenu=None)
        self.curv_canal=list()
        self.curv_canal.append(self.pg_widget.plot(pen='r'))  
        self.curv_canal.append(self.pg_widget.plot(pen='y'))  
        self.curv_canal.append(self.pg_widget.plot(pen='g'))  
        self.curv_canal.append(self.pg_widget.plot(pen='c'))
        self.set_canal=list()
        self.set_canal.append(self.c_canal1)
        self.set_canal.append(self.c_canal2)
        self.set_canal.append(self.c_canal3)
        self.set_canal.append(self.c_canal4)
        self.tet_selec=1
        

class mymenu(QtGui.QMenu):  
    def __init__(self):
        QtGui.QMenu.__init__(self)  
              
        self.opciones=uic.loadUi(uifile_menu)
        self.setTitle("Opciones")   
           
        aux= QtGui.QWidgetAction(self);
        aux.setDefaultWidget(self.opciones);
        self.addAction(aux)
