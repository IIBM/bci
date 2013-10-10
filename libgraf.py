from pyqtgraph.Qt import QtGui, QtCore #interfaz en general
import pyqtgraph as pg #graficos
import os
from PyQt4  import uic
from scipy import signal
import numpy as np
import config

uifile_menu = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'menu.ui') 

uifile_dialog = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'tet_dialog.ui')

ch_colors=['r','y','g','c']


pasa_bajos=signal.firwin(61, 0.01)
pasa_altos=signal.firwin(61, 0.01, pass_zero=False)
subm=25
xtime=np.arange(0,float(config.CANT_DISPLAY)/float(config.FS),subm/float(config.FS))
fft_frec= np.linspace(0, config.FS/2, config.CANT_DISPLAY/2/subm)
xtime_dialog=np.linspace(0,float(config.CANT_DISPLAY)/float(config.FS),config.CANT_DISPLAY)
fft_frec_dialog= np.linspace(0, config.FS/2, config.CANT_DISPLAY/2)

class  tets_display():
    def __init__(self,espacio_pg):
        layout_graficos = pg.GraphicsLayout() #para ordenar los graficos(items) asi como el simil con los widgets
        espacio_pg.setCentralItem(layout_graficos)
        
        self.set_canales=list() #canales seleccionados para ser mostrados
        self.s_modes=list() #estado del boton con el tipo de curva(fft, etc)
        self.curv_canal=list() #curvas para dsp actualizar los datos
        self.graficos=list() #graficos, para dsp poder modificar su autorange
        self.offset_cc=list()
        #graficos principales    

        for i in range((config.CANT_CANALES+3)/4):
            graf = layout_graficos.addPlot(row=None, col=None, rowspan=1, colspan=1)
            graf.setTitle('Tetrodo ' + str(i+1))
            graf.ctrlMenu = mymenu()
            
            self.set_canales.append(graf.ctrlMenu.opciones.cb_c1)
            self.set_canales.append(graf.ctrlMenu.opciones.cb_c2)
            self.set_canales.append(graf.ctrlMenu.opciones.cb_c3)
            self.set_canales.append(graf.ctrlMenu.opciones.cb_c4)
            
            self.s_modes.append(graf.ctrlMenu.opciones.s_filtro)
            self.offset_cc.append(graf.ctrlMenu.opciones.offset_cc)
            self.curv_canal.append(graf.plot(pen=ch_colors[0]))  
            self.curv_canal.append(graf.plot(pen=ch_colors[1]))  
            self.curv_canal.append(graf.plot(pen=ch_colors[2]))  
            self.curv_canal.append(graf.plot(pen=ch_colors[3]))
            self.graficos.append(graf)
            if not (i+1)%4:
                layout_graficos.nextRow()
                
    def update(self,data):    
        canales_mostrados_sf = list()
        canales_pasa_bajos = list()
        canales_pasa_altos = list()
        canales_fft = list()
        
        for i in range(config.CANT_CANALES):
            if self.set_canales[i].isChecked() == 0:
                self.curv_canal[i].clear()
            elif self.s_modes[i/4].currentIndex() ==0:
                canales_mostrados_sf.append(i)
            elif self.s_modes[i/4].currentIndex() ==1:
                canales_pasa_bajos.append(i)
            elif self.s_modes[i/4].currentIndex() ==2:
                canales_pasa_altos.append(i)
            else:
                canales_fft.append(i)

        for i in canales_mostrados_sf:
            self.curv_canal[i].setData(x=xtime,y=data[i,::subm]+self.offset_cc[i/4].value()*i%4, _callSync='off')
        
        if len(canales_pasa_bajos) !=0:
            aux=signal.lfilter(pasa_bajos, 1,data[canales_pasa_bajos,:]) 
            for i in range(len(canales_pasa_bajos)):
                self.curv_canal[canales_pasa_bajos[i]].setData(x=xtime,y=aux[i,::subm]+self.offset_cc[i/4].value()*i%4, _callSync='off')
        
        if len(canales_pasa_altos) !=0:
            aux=signal.lfilter(pasa_altos, 1,data[canales_pasa_altos,:]) 
            for i in range(len(canales_pasa_altos)):
                self.curv_canal[canales_pasa_altos[i]].setData(x=xtime,y=aux[i,::subm]+self.offset_cc[i/4].value()*i%4, _callSync='off')    
        
        if len(canales_fft) !=0:
            aux=np.fft.fft(data[canales_fft,:]) #/config.CANT_DISPLAY
            aux = abs(aux[:,:np.size(aux,1)/2:subm])
            for i in range(len(canales_fft)):
                self.curv_canal[canales_fft[i]].setData(x=fft_frec,y=aux[i,:]+self.offset_cc[i/4].value()*i%4, _callSync='off')  

    
    def setAutoRange(self,state):
        for grafico in self.graficos:
            grafico.enableAutoRange('xy', state)  
                


class  rates_display():
    def __init__(self,ecualizer_grid,dialogo):
        layout_ecualizer= pg.GraphicsLayout() #para ordenar los graficos(items) asi como el simil con los widgets            
        ecualizer_grid.setCentralItem(layout_ecualizer)
        
        self.tasa_bars=list()
        self.tasa_graf=list()
        for i in range((config.CANT_CANALES)/4):
            graf=bar_graf(i,self.tasa_bars,dialogo)
            layout_ecualizer.addItem(graf,row=None, col=None, rowspan=1, colspan=1)
            self.tasa_graf.append(graf)
    def update(self,tasas):
            for i in range(len(self.tasa_bars)):
                self.tasa_bars[i].setData(x=[i%4-0.3,i%4+0.3],y=[tasas[i],tasas[i]], _callSync='off')
    
    def change_scale(self,scale):
        for bar in self.tasa_graf:
            bar.setYRange(0, scale)





class  bar_graf(pg.PlotItem):
    def __init__(self,i,tasa_bars,dialogo):
        vb=ViewBox_Bars(i,dialogo)
        pg.PlotItem.__init__(self,viewBox=vb,title="Tet."+str(i+1))
        self.showAxis('bottom', False)
        self.setMenuEnabled(enableMenu=False)
        self.showAxis('left', False)
        self.enableAutoRange('y', False)
        self.setXRange(-0.4,3+0.4)
        self.enableAutoRange('x', False)
        self.setYRange(0, 500)
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()
        tasa_bars.append(self.plot(pen='r', fillLevel=0,brush=pg.mkBrush(ch_colors[0])))
        tasa_bars.append(self.plot(pen='y', fillLevel=0,brush=pg.mkBrush(ch_colors[1])))
        tasa_bars.append(self.plot(pen='g', fillLevel=0,brush=pg.mkBrush(ch_colors[2])))
        tasa_bars.append(self.plot(pen='c', fillLevel=0,brush=pg.mkBrush(ch_colors[3])))     
        
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
        self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[0]))  
        self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[1]))  
        self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[2]))  
        self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[3]))
        self.set_canal=list()
        self.set_canal.append(self.c_canal1)
        self.set_canal.append(self.c_canal2)
        self.set_canal.append(self.c_canal3)
        self.set_canal.append(self.c_canal4)
        self.tet_selec=1
    
    def update(self,data):
        if self.isVisible():
            self.num_tet.setText('Tetrodo: '+str(1+self.tet_selec))
            tet=self.tet_selec
            canal=range(tet*4,tet*4+4)
            for i in range(len(self.set_canal)):
                if not self.set_canal[i].isChecked():
                    self.curv_canal[i].clear()
                elif self.normal.isChecked():
                    self.curv_canal[i].setData(x=xtime_dialog,y=i*self.offsetcc.value()+data[canal[i],:])
                elif self.pasaaltos.isChecked():
                    self.curv_canal[i].setData(x=xtime_dialog,y=i*self.offsetcc.value()+signal.lfilter(pasa_bajos, 1,data[canal[i],:]))
                elif self.pasabajos.isChecked():
                    self.curv_canal[i].setData(x=xtime_dialog,y=i*self.offsetcc.value()+signal.lfilter(pasa_altos, 1,data[canal[i],:]))
                else:
                    aux=np.fft.fft(data[canal[i],:]) #/config.CANT_DISPLAY
                    self.curv_canal[i].setData(x=fft_frec_dialog,y=i*self.offsetcc.value()*1000+abs(aux[:np.size(aux)/2]))

        

class mymenu(QtGui.QMenu):  
    def __init__(self):
        QtGui.QMenu.__init__(self)  
              
        self.opciones=uic.loadUi(uifile_menu)
        self.setTitle("Opciones")   
           
        aux= QtGui.QWidgetAction(self);
        aux.setDefaultWidget(self.opciones);
        self.addAction(aux)
