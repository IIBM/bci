from pyqtgraph.Qt import QtCore #interfaz en general
import pyqtgraph as pg #graficos
import os
from PyQt4  import QtGui,uic
from scipy import signal,fftpack
import numpy as np
import config
from data_processing import calcular_umbral_disparo,calcular_tasa_disparo

#uifile_menu = os.path.join(
    #os.path.abspath(
        #os.path.dirname(__file__)),'menu.ui') 

#uifile_dialog = os.path.join(
    #os.path.abspath(
        #os.path.dirname(__file__)),'tet_dialog.ui')

second_win_file = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'second_window.ui')

ch_colors=['r','y','g','c']

FFT_L=8192*2 #largo del vector con el q se realiza fft
FFT_N=4  #cantidad de ffts q se promedian
FFT_L_PAQ=3 #cantidad de paqueques q se concatenan para fft
numero_filas_tet_display=3
#pasa_bajos=signal.firwin(61, 0.01)
#pasa_altos=signal.firwin(61, 0.01, pass_zero=False)
subm=1
#fft_frec= np.linspace(0, config.FS/2, config.CANT_DISPLAY/2/subm)
#xtime_dialog=np.linspace(0,float(config.CANT_DISPLAY)/float(config.FS),config.CANT_DISPLAY)
fft_frec= np.linspace(0, config.FS/2, FFT_L/2)
ESCALA_DISPLAY=200
TWO_WINDOWS=True

#class tets_display():
    #def __init__(self,espacio_pg):
        #layout_graficos = pg.GraphicsLayout() #para ordenar los graficos(items) asi como el simil con los widgets
        #espacio_pg.setCentralItem(layout_graficos)
        
        #self.set_canales=list() #canales seleccionados para ser mostrados
        #self.s_modes=list() #estado del boton con el tipo de curva(fft, etc)
        #self.curv_canal=list() #curvas para dsp actualizar los datos
        #self.graficos=list() #graficos, para dsp poder modificar su autorange
        #self.offset_cc=list()
        ##graficos principales

        #for i in range((config.CANT_CANALES+3)/4):
            #graf = layout_graficos.addPlot(row=None, col=None, rowspan=1, colspan=1)
            #graf.setTitle('Tetrodo ' + str(i+1))
            #graf.ctrlMenu = mymenu()
            
            #self.set_canales.append(graf.ctrlMenu.opciones.cb_c1)
            #self.set_canales.append(graf.ctrlMenu.opciones.cb_c2)
            #self.set_canales.append(graf.ctrlMenu.opciones.cb_c3)
            #self.set_canales.append(graf.ctrlMenu.opciones.cb_c4)
            
            #self.s_modes.append(graf.ctrlMenu.opciones.s_filtro)
            #self.offset_cc.append(graf.ctrlMenu.opciones.offset_cc)
            #self.curv_canal.append(graf.plot(pen=ch_colors[0]))
            #self.curv_canal.append(graf.plot(pen=ch_colors[1]))
            #self.curv_canal.append(graf.plot(pen=ch_colors[2]))
            #self.curv_canal.append(graf.plot(pen=ch_colors[3]))
            #self.graficos.append(graf)
            #if not (i+1)%numero_filas_tet_display:
                #layout_graficos.nextRow()
                
    #def update(self,data):
        #canales_mostrados_sf = list()
        #canales_pasa_bajos = list()
        #canales_pasa_altos = list()
        #canales_fft = list()
        
        #for i in range(config.CANT_CANALES):
            #if self.set_canales[i].isChecked() == 0:
                #self.curv_canal[i].clear()
            #elif self.s_modes[i/4].currentIndex() ==0:
                #canales_mostrados_sf.append(i)
            #elif self.s_modes[i/4].currentIndex() ==1:
                #canales_pasa_bajos.append(i)
            #elif self.s_modes[i/4].currentIndex() ==2:
                #canales_pasa_altos.append(i)
            #else:
                #canales_fft.append(i)
        
        #for i in canales_mostrados_sf:
            #self.curv_canal[i].setData(x=xtime,y=data[i,::subm]+self.offset_cc[i/4].value()*(i%4), _callSync='off')
        #if len(canales_pasa_bajos) !=0:
            #aux=signal.lfilter(pasa_bajos, 1,data[canales_pasa_bajos,:])
            #for i in range(len(canales_pasa_bajos)):
                #self.curv_canal[canales_pasa_bajos[i]].setData(x=xtime,y=aux[i,::subm]+self.offset_cc[i/4].value()*(i%4), _callSync='off')
        
        #if len(canales_pasa_altos) !=0:
            #aux=signal.lfilter(pasa_altos, 1,data[canales_pasa_altos,:])
            #for i in range(len(canales_pasa_altos)):
                #self.curv_canal[canales_pasa_altos[i]].setData(x=xtime,y=aux[i,::subm]+self.offset_cc[i/4].value()*(i%4), _callSync='off')
        
        #if len(canales_fft) !=0:
            #aux=np.fft.fft(data[canales_fft,:]) #/config.CANT_DISPLAY
            #aux = abs(aux[:,:np.size(aux,1)/2:subm])
            #for i in range(len(canales_fft)):
                #self.curv_canal[canales_fft[i]].setData(x=fft_frec,y=aux[i,:]+self.offset_cc[i/4].value()*(i%4), _callSync='off')

    
    #def setAutoRange(self,state):
        #for grafico in self.graficos:
            #grafico.enableAutoRange('xy', state)  
                
class  plus_display():
    def __init__(self,espacio_pg,plus_grid_fr,c_auto_umbral,c_manual_umbral,beepbox): 
        #self.tmodes=np.ones(config.CANT_CANALES) #modos por defecto en 1, osea en auto
        self.tmode_auto=list([True for i in range(config.CANT_CANALES)]) #modos por defecto, en 2 es AUTO check
        self.umbrales_manuales=np.zeros(config.CANT_CANALES)
        self.mode=0
        self.c_auto_umbral=c_auto_umbral
        self.c_manual_umbral=c_manual_umbral
        #layout_graficos = pg.GraphicsLayout() #para ordenar los graficos(items) asi como el simil con los widgets
        self.beepbox=beepbox
        self.selec_canal=0 #HARDCODE
        self.selec_tet=0  #HARDCODE
        
        self.tasas_bars=bar_graf()
        #layout_graficos.addItem(self.tasas_bars,row=None, col=0, rowspan=1, colspan=1)
        #graf=layout_graficos.addPlot(row=None, col=1, rowspan=1, colspan=3)
        self.graf = pg.PlotItem()
        self.VB=self.graf.getViewBox()
        self.VB.setXRange(0, config.PAQ_USB/float(config.FS), padding=0, update=True)
        self.VB.setYRange(ESCALA_DISPLAY,-ESCALA_DISPLAY, padding=0, update=True)
        self.graf.setMenuEnabled(enableMenu=False,enableViewBoxMenu=None)
        self.graf.setDownsampling(auto=True)
        self.curve=self.graf.plot()
        self.graf_umbral=pg.InfiniteLine(pen='b',angle=0,movable=False)
        self.graf.enableAutoRange('y', False)
        espacio_pg.setCentralItem(self.graf)
        plus_grid_fr.setCentralItem(self.tasas_bars)
        self.fft_n=0
        self.data_fft=0
        self.fft_l=0
        self.fft_aux=np.zeros([FFT_N,FFT_L/2])
        self.data_fft_aux=np.zeros([config.PAQ_USB*FFT_L_PAQ])
        self.graf.addItem(self.graf_umbral)
        
    def update(self,data,data_new,n_view,xtime):
        
        if self.tmode_auto[self.selec_canal+4*self.selec_tet] is False:
            self.umbrales_manuales[self.selec_tet*4+self.selec_canal]=self.graf_umbral.value()
        self.max_xtime=xtime[n_view-1]
        tasas=np.zeros([4])
        #reordenar esto, se calculan medianas q podrian no estarse usando.MEJORAR
        #x,umbral_calc=calcular_umbral_disparo(data[:,:n_view],range(4*self.selec_tet,4*self.selec_tet+4))
        
        
        #for i in range(4):
            #if self.tmode_auto[4*self.selec_tet+i] is True:
                #tasas[i]=calcular_tasa_disparo(x[i,:],umbral_calc[i])
                
            #else:       
                #tasas[i]=calcular_tasa_disparo(x[i,:],self.umbrales_manuales[4*self.selec_tet+i])
        
        for i in range(4):
            tasas[i]=calcular_tasa_disparo(data_new[i,:],self.umbrales_manuales[4*self.selec_tet+i])
        
        if tasas[self.selec_canal] > 0 and self.beepbox.isChecked():
            #print '\a' 
            os.system("beep -f 700 -l 18 &")
        self.tasas_bars.update(tasas)
        #self.curve.setPen(ch_colors[self.selec_canal])
        if self.mode is 0:
            #self.VB.setXRange(0, xtime[n_view-1], padding=0, update=False)
            self.curve.setPen(ch_colors[self.selec_canal])
            self.curve.setData(x=xtime[:n_view],y=data[self.selec_tet*4+self.selec_canal,:n_view])
        #elif self.mode is 1:  
            #self.curve.setPen(ch_colors[self.selec_canal])
            ##self.VB.setXRange(0, xtime[n_view-1], padding=0, update=False)
            #self.curve.setData(x=xtime[:n_view],y=x[self.selec_canal,:n_view], _callSync='off')
            #if self.tmode_auto[self.selec_canal+4*self.selec_tet] is True:
                #self.graf_umbral.setValue(umbral_calc[self.selec_canal])
            
        else:
            if( self.fft_l < FFT_L_PAQ):
                self.data_fft_aux[self.fft_l*config.PAQ_USB:(1+self.fft_l)*config.PAQ_USB]=data_new[self.selec_tet*4+self.selec_canal,:]
                self.fft_l+=1
            else:
                self.fft_l=0
                if (self.fft_n <FFT_N):
                    self.fft_aux[self.fft_n,:]=abs(fftpack.fft(self.data_fft_aux,n=FFT_L)[:FFT_L/2])** 2. / float(FFT_L)
                    self.fft_n+=1
                else:
                    self.fft_n=0
                    self.curve.setPen(ch_colors[self.selec_canal])
                    self.curve.setData(x=fft_frec,y=np.mean(self.fft_aux,0))
                    
            #aux=fftpack.fft(data[self.selec_tet*4+self.selec_canal,:],n=FFT_L) #/config.CANT_DISPLAY
            #self.curve.setData(x=fft_frec,y=abs(aux[:np.size(aux)/2]))
        
        return [self.selec_tet,self.selec_canal]
    def change_display_mode(self,new_mode):
        
        if new_mode is 0:
            self.graf.addItem(self.graf_umbral)
            self.VB.setXRange(0, self.max_xtime, padding=0, update=False)
            #self.graf.setLogMode(x=False,y=False)
            if(self.mode is 1):
                self.graf.removeItem(self.graf_umbral)
            
        #elif new_mode is 1:
            #self.graf.addItem(self.graf_umbral)
            #self.VB.setXRange(0, self.max_xtime, padding=0, update=False)
            ##self.VB.setXRange(0, self_max_xtime, padding=0, update=False)
            ##self.graf.setLogMode(x=False,y=False)
            
            if self.tmode_auto[self.selec_canal+4*self.selec_tet] is False:
                self.graf_umbral.setValue(self.umbrales_manuales[self.selec_tet*4+self.selec_canal])
                self.graf_umbral.setMovable(True)

        else: 
            #self.graf.setLogMode(x=True,y=True)
            self.VB.setXRange(0, config.FS/2, padding=0, update=False)
            if(self.mode is 0):
                self.graf.removeItem(self.graf_umbral)
            self.fft_l=0
            self.fft_n=0    
            #self.curve.setData(x=[0],y=[0])
        self.mode=new_mode
        self.change_line_mode()
        
        
    def change_channel(self,canal):
        self.selec_tet=int(canal/4)
        self.selec_canal=canal%4
        self.c_auto_umbral.setCheckState(2* self.tmode_auto[canal])
        self.c_manual_umbral.setCheckState(2*(not self.tmode_auto[canal]))
        self.change_line_mode()
        self.fft_l=0
        self.fft_n=0
        
    def change_tmode(self,new_mode):
        self.tmode_auto[self.selec_canal+4*self.selec_tet]=(new_mode is 2)
        self.change_line_mode()
    
    def change_line_mode(self):
        if self.tmode_auto[self.selec_canal+4*self.selec_tet] is False:
            self.graf_umbral.setMovable(True)
            self.graf_umbral.setValue(self.umbrales_manuales[self.selec_tet*4+self.selec_canal])
        else:
            self.graf_umbral.setMovable(False)
        
            
#class  rates_display():
    #def __init__(self,ecualizer_grid,dialogo):
        #layout_ecualizer= pg.GraphicsLayout() #para ordenar los graficos(items) asi como el simil con los widgets            
        #ecualizer_grid.setCentralItem(layout_ecualizer)
        
        #self.tasa_bars=list()
        #self.tasa_graf=list()
        #for i in range((config.CANT_CANALES+3)/4):
            #graf=bar_graf(i,self.tasa_bars,dialogo)
            #layout_ecualizer.addItem(graf,row=None, col=None, rowspan=1, colspan=1)
            #self.tasa_graf.append(graf)
    #def update(self,tasas):
            #for i in range((config.CANT_CANALES)/4*4):
                #self.tasa_bars[i].setData(x=[i%4-0.3,i%4+0.3],y=[tasas[i],tasas[i]], _callSync='off')
    
    #def change_scale(self,scale):
        #for bar in self.tasa_graf:
            #bar.setYRange(0, scale)



#class  bar_graf(pg.PlotItem):
    #def __init__(self,i,tasa_bars,dialogo):
        #vb=ViewBox_Bars(i,dialogo)
        #pg.PlotItem.__init__(self,viewBox=vb,title="Tet."+str(i+1))
        #self.showAxis('bottom', False)
        #self.setMenuEnabled(enableMenu=False)
        #self.showAxis('left', False)
        #self.enableAutoRange('y', False)
        #self.setXRange(-0.4,3+0.4)
        #self.enableAutoRange('x', False)
        #self.setYRange(0, 500)
        #self.setMouseEnabled(x=False, y=False)
        #self.hideButtons()
        #tasa_bars.append(self.plot(pen='r', fillLevel=0,brush=pg.mkBrush(ch_colors[0])))
        #tasa_bars.append(self.plot(pen='y', fillLevel=0,brush=pg.mkBrush(ch_colors[1])))
        #tasa_bars.append(self.plot(pen='g', fillLevel=0,brush=pg.mkBrush(ch_colors[2])))
        #tasa_bars.append(self.plot(pen='c', fillLevel=0,brush=pg.mkBrush(ch_colors[3])))     
        
#class ViewBox_Bars(pg.ViewBox):
    #def __init__(self,i,dialogo):
        #pg.ViewBox.__init__(self)
        #self.canal=i
        #self.dialogo=dialogo
    #def mouseClickEvent(self, ev):
        #if ev.button() == QtCore.Qt.LeftButton:
            #self.dialogo.show()
            #self.dialogo.tet_selec=self.canal

#class Dialog_Tet(QtGui.QDialog):
    ##Ventana extra que se abre al clickear las barras        
    #def __init__(self):
        #QtGui.QDialog.__init__(self)
        #uic.loadUi(uifile_dialog,self)
        #self.setWindowFlags(QtCore.Qt.Window) 
        #self.pg_widget.setMenuEnabled(enableMenu=False,enableViewBoxMenu=None)
        #self.curv_canal=list()
        #self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[0]))  
        #self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[1]))  
        #self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[2]))  
        #self.curv_canal.append(self.pg_widget.plot(pen=ch_colors[3]))
        #self.set_canal=list()
        #self.set_canal.append(self.c_canal1)
        #self.set_canal.append(self.c_canal2)
        #self.set_canal.append(self.c_canal3)
        #self.set_canal.append(self.c_canal4)
        #self.tet_selec=1
    
    #def update(self,data):
        #if self.isVisible():
            #self.num_tet.setText('Tetrodo: '+str(1+self.tet_selec))
            #tet=self.tet_selec
            #canal=range(tet*4,tet*4+4)
            #for i in range(len(self.set_canal)):
                #if not self.set_canal[i].isChecked():
                    #self.curv_canal[i].clear()
                #elif self.normal.isChecked():
                    #self.curv_canal[i].setData(x=xtime_dialog,y=i*self.offsetcc.value()+data[canal[i],:])
                #elif self.pasaaltos.isChecked():
                    #self.curv_canal[i].setData(x=xtime_dialog,y=i*self.offsetcc.value()+signal.lfilter(pasa_bajos, 1,data[canal[i],:]))
                #elif self.pasabajos.isChecked():
                    #self.curv_canal[i].setData(x=xtime_dialog,y=i*self.offsetcc.value()+signal.lfilter(pasa_altos, 1,data[canal[i],:]))
                #else:
                    #aux=np.fft.fft(data[canal[i],:]) #/config.CANT_DISPLAY
                    #self.curv_canal[i].setData(x=fft_frec_dialog,y=i*self.offsetcc.value()*1000+abs(aux[:np.size(aux)/2]))

        

#class mymenu(QtGui.QMenu):  
    #def __init__(self):
        #QtGui.QMenu.__init__(self)  
              
        #self.opciones=uic.loadUi(uifile_menu)
        #self.setTitle("Opciones")   
           
        #aux= QtGui.QWidgetAction(self);
        #aux.setDefaultWidget(self.opciones);
        #self.addAction(aux)


class  bar_graf(pg.PlotItem):
    def __init__(self):
        self.tasa_bars=list()
        pg.PlotItem.__init__(self)
        self.showAxis('bottom', False)
        self.setMenuEnabled(enableMenu=False,enableViewBoxMenu=None)
        #self.showAxis('left', False)
        #self.enableAutoRange('y', False)
        self.setXRange(-0.4,3+0.4)
        self.enableAutoRange('x', False)
        #self.setYRange(0, 500)
        self.setMouseEnabled(x=False, y=True)
        #self.hideButtons()
        self.tasa_bars.append(self.plot(pen=ch_colors[0], fillLevel=0,brush=pg.mkBrush(ch_colors[0])))
        self.tasa_bars.append(self.plot(pen=ch_colors[1], fillLevel=0,brush=pg.mkBrush(ch_colors[1])))
        self.tasa_bars.append(self.plot(pen=ch_colors[2], fillLevel=0,brush=pg.mkBrush(ch_colors[2])))
        self.tasa_bars.append(self.plot(pen=ch_colors[3], fillLevel=0,brush=pg.mkBrush(ch_colors[3])))

    def update(self,tasas):
            for i in range(4):
                self.tasa_bars[i].setData(x=[i%4-0.3,i%4+0.3],y=[tasas[i],tasas[i]], _callSync='off')

        
class general_display():
    def __init__(self,espacio_pg,info_tet):
        layout_graficos = pg.GraphicsLayout(border=(100,0,100)) #para ordenar los graficos(items) asi como el simil con los widgets
        espacio_pg.setCentralItem(layout_graficos)
        #self.vieboxs=list()
        self.set_canales=list() #canales seleccionados para ser mostrados
        self.curv_canal=list() #curvas para dsp actualizar los datos
        self.graficos=list() #graficos, para dsp poder modificar su autorange
        #graficos principales
        
        
        if TWO_WINDOWS is False:
            main_win_ch=config.CANT_CANALES
    
        else:
            main_win_ch=int(config.CANT_CANALES*3/4/7)*4
            self.second_win=Second_Display_Window()            
            layout_graficos_2=self.second_win.layout_graficos
            self.second_win.show()
            
        for i in range(config.CANT_CANALES):
            vb=ViewBox_General_Display(i,info_tet)
            
            if (i < main_win_ch):
                graf = layout_graficos.addPlot(viewBox=vb,row=int(i/4/numero_filas_tet_display)*4+i%4, col=int(i/4)%numero_filas_tet_display, rowspan=1, colspan=1)
            else:
                graf = layout_graficos_2.addPlot(viewBox=vb,row=int((i-main_win_ch)/4/numero_filas_tet_display)*4+(i-main_win_ch)%4, col=int((i-main_win_ch)/4)%numero_filas_tet_display, rowspan=1, colspan=1)
            
            graf.hideButtons()
            graf.setDownsampling(auto=True)
            
            VB=graf.getViewBox()
            VB.setXRange(0, float(config.CANT_DISPLAY)/float(config.FS), padding=0, update=True) #HARDCODE
            VB.setYRange(ESCALA_DISPLAY,-ESCALA_DISPLAY, padding=0, update=True)
            #self.vieboxs.append(VB)
            if i%4 is 0:
                graf.setTitle('Tetrodo ' + str(i/4+1))
            #if i%4 != 3:
                #graf.showAxis('bottom', show=False)
            graf.showAxis('bottom', show=False) 
            graf.showAxis('top', show=False)
            graf.showAxis('right', show=False)
            graf.showAxis('left', show=False)
            graf.showGrid(y=True)
            graf.setMenuEnabled(enableMenu=False,enableViewBoxMenu=False)
            graf.setMouseEnabled(x=False, y=False)
            self.curv_canal.append(graf.plot())
            self.curv_canal[-1].setPen(width=1,color=ch_colors[i%4])
            self.graficos.append(graf)
        #self.casa=4
        
        
    def change_Yrange(self,p):
        p=float(p)/10
        for i in range(config.CANT_CANALES):
           self.graficos[i].setYRange(ESCALA_DISPLAY*p,-1*ESCALA_DISPLAY*p, padding=0, update=False)
    
    
    def changeXrange(self,i):
        max_x=i*config.PAQ_USB/float(config.FS)
        for i in range(config.CANT_CANALES):
            self.graficos[i].setXRange(0,max_x, padding=0, update=False)
            
        
    def update(self,data,n_view,xtime):
        #self.casa+=1
        #step=config.PAQ_USB/float(config.FS)/4
        #if self.casa >= 4:
        for i in range(config.CANT_CANALES):
            self.curv_canal[i].setData(x=xtime[:n_view:subm],y=data[i,:n_view:subm])
            #self.casa=0               
        #for i in range(config.CANT_CANALES):
           # self.vieboxs[i].setXRange(self.casa*step,(self.casa+1)*step, padding=0, update=False)
    #def setAutoRange(self,state):
        #for grafico in self.graficos:
            #grafico.enableAutoRange('xy', state)  
    def close(self):
        if TWO_WINDOWS is True:
            self.second_win.Close()
            
class ViewBox_General_Display(pg.ViewBox):
    def __init__(self,i,info_tet):
        pg.ViewBox.__init__(self)
        self.i=i
        self.info_tet=info_tet
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.info_tet.change_channel(self.i)
            
class Second_Display_Window(QtGui.QDialog):
    ##Ventana extra
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi(second_win_file,self)
        self.setWindowFlags(QtCore.Qt.Window)
        self.layout_graficos = pg.GraphicsLayout(border=(100,0,100)) #para ordenar los graficos(items) asi como el simil con los widgets
        self.graphicsView.setCentralItem(self.layout_graficos)
        self.closeable=False
    
    def Close(self):
        self.closeable=True
        self.close()
        
    def closeEvent(self, evnt):
        if self.closeable is False:
            evnt.ignore()
            
        
