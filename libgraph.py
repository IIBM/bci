from pyqtgraph.Qt import QtCore #interfaz en general
import pyqtgraph as pg #graphicos
from PyQt4  import QtGui,uic
from scipy import signal,fftpack
import numpy as np
import config
import time
import threading
import copy
from multiprocess_config import *
from libgraph_config import *
from spikes_config import spike_duration
     
spike_duration_samples=int(spike_duration/1000.0*config.FS)

fft_frec= np.linspace(0, config.FS/2, FFT_L/2)
one_pack_time=config.PAQ_USB/config.FS
PACK_xSPIKE_COUNT=int(float(TIME_SPIKE_COUNT)/one_pack_time)
FREQFIX_xSPIKE_COUNT=(float(PACK_xSPIKE_COUNT)*one_pack_time)
beep_command="beep -f " + BEEP_FREQ + " -l " + str(spike_duration) + " -d "

class MainWindow(QtGui.QMainWindow):
    def __init__(self,processing_process,get_data_process,generic_file):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.generic_file=generic_file
        #self.tet_plus_selec
        #diagolo q da mas info del canal
        #self.dialogo=Dialog_Tet()
        #self.matriz_tetrodos=tets_display(self.espacio_pg)
        #for i in range((config.CANT_CANALES)/4):
            #self.tet_plus_selec.addItem('T%s' % (i + 1))
        self.processing_process=processing_process
        self.get_data_process=get_data_process
        self.signal_config=Config_processing(False,DISPLAY_LIMY/2*np.ones([config.CANT_CANALES,1])) #HARDCODE
        self.active_channels=[False for j in range(config.CANT_CANALES)]
        try:
            processing_process.ui_config_queue.put(self.signal_config)
        except:
            pass
        self.info_tetrodo=plus_display(self.plus_grid,self.plus_grid_fr,self.signal_config)
        self.matriz_tetrodos=general_display(self.espacio_pg,self.info_tetrodo)
        self.data_handler=bci_data_handler()
        #QtCore.QObject.connect(self.autoRange, QtCore.SIGNAL("clicked()"), self.set_autoRange)
        QtCore.QObject.connect(self.tet_plus_mode, QtCore.SIGNAL("currentIndexChanged(int)"), self.info_tetrodo.change_display_mode) 
        #QtCore.QObject.connect(self.c_auto_umbral, QtCore.SIGNAL("stateChanged(int)"), self.info_tetrodo.change_tmode) 
        QtCore.QObject.connect(self.display_scale, QtCore.SIGNAL("valueChanged(int)"), self.matriz_tetrodos.change_Yrange)  
        QtCore.QObject.connect(self.paq_view, QtCore.SIGNAL("valueChanged(int)"), self.changeXrange)  
        QtCore.QObject.connect(self.active_channel_cb, QtCore.SIGNAL("clicked( bool)"),self.activate_channel)
        self.get_data_warning_time=0
        self.processing_process_warning_time=0
        self.file_label.setText(NOT_SAVING_MESSAGE)
        self.contador_registro=-1
        self.timer = QtCore.QTimer()
        
        self.timer.timeout.connect(self.update)
        processing_process.process.start()
        get_data_process.process.start()
        self.timer.start(0) #si va demasiado lento deberia bajarse el tiempo
        self.t1 = time.time()
        
    def update(self):
        #check if get_data process can send data

        self.signal_config.filter_mode= self.filter_mode_button.isChecked()
        
        try:
            self.data_handler.update(self.processing_process.new_data_queue.get(TIMEOUT_GET),self.signal_config.filter_mode)
        except:
            return 1
        if (not self.get_data_process.warnings.empty()):
            self.get_data_warning_time=time.time()
            self.warnings.setText(Errors_Messages[self.get_data_process.warnings.get(TIMEOUT_GET)])
        else:
            if(time.time()-self.get_data_warning_time > MESSAGE_TIME):
                self.warnings.setText("") 
        
        if (not self.processing_process.warnings.empty()):
            self.processing_process_warning_time=time.time()
            self.status.setText(Errors_Messages[self.processing_process.warnings.get(TIMEOUT_GET)])
        else:
            if(time.time()-self.processing_process_warning_time > MESSAGE_TIME):
                self.status.setText("")                  
            
            
        if self.beepbox.isChecked():
            t = threading.Thread(target=beep,args=[self.data_handler.spikes_times[self.info_tetrodo.channel]])
            t.start()    
                   
        self.update_graphicos()
        try:
            self.processing_process.ui_config_queue.put(self.signal_config)
        except:
            pass
        
    def update_graphicos(self):    
        #self.dialogo.update(self.data)
        #self.matriz_tasas.update(self.tasas_disparo)
        self.matriz_tetrodos.update(self.data_handler.graph_data,self.data_handler.n_view)
        self.info_tetrodo.update(self.data_handler,self.pausa.isChecked())
        self.info_label.setText('TET:'+str(int(self.info_tetrodo.channel/4)+1)+' C:'+str(self.info_tetrodo.channel%4+1))
        self.active_channel_cb.setChecked(self.active_channels[self.info_tetrodo.channel])
    
    def on_actionDetener(self):
        #detiene el guardado de datos
        self.get_data_process.control.send(STOP_SIGNAL)
        self.file_label.setText(NOT_SAVING_MESSAGE)

    def on_actionSalir(self):
        self.timer.stop()
        self.get_data_process.control.send(EXIT_SIGNAL)
        self.processing_process.control.send(EXIT_SIGNAL)
        self.get_data_process.process.join(1)
        self.processing_process.process.join(1)
        self.get_data_process.process.join(1)
        self.processing_process.process.terminate()
        self.get_data_process.process.terminate()
        self.matriz_tetrodos.close()
        self.close()
       
    def on_actionNuevo(self):
        self.get_data_process.control.send(START_SIGNAL)
        self.contador_registro+=1
        self.file_label.setText(SAVING_MESSAGE + self.generic_file +'-'+str(self.contador_registro))


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
    
    def activate_channel(self,i):
        self.active_channels[self.info_tetrodo.channel]=i
        
    def on_actionInit_SP(self):
        self.active_channel_cb.setCheckable(False)
        self.processing_process.control.send(active_channels)
        pass #FER termina esto
    #@QtCore.pyqtSlot()          
    #def on_s_canal1_valueChanged(self,int):
        #print str(self.s_canal1.value())

                
class  plus_display():
    def __init__(self,espacio_pg,plus_grid_fr,signal_config): 
        #self.tmodes=np.ones(config.CANT_CANALES) #modos por defecto en 1, osea en auto
        #self.tmode_auto=list([False for i in range(config.CANT_CANALES)]) #modos por defecto, en 2 es AUTO check
        self.mode=0
        #self.c_auto_umbral=c_auto_umbral
        #self.c_manual_umbral=c_manual_umbral
        self.channel=0
        #layout_graphicos = pg.GraphicsLayout() #para ordenar los graphicos(items) asi como el simil con los widgets
        self.signal_config=signal_config
        self.tasas_bars=bar_graph()
        #layout_graphicos.addItem(self.tasas_bars,row=None, col=0, rowspan=1, colspan=1)
        #graph=layout_graphicos.addPlot(row=None, col=1, rowspan=1, colspan=3)
        self.graph = pg.PlotItem()
        self.VB=self.graph.getViewBox()
        self.VB.setXRange(0, config.PAQ_USB/float(config.FS), padding=0, update=True)
        self.VB.setYRange(DISPLAY_LIMY,-DISPLAY_LIMY, padding=0, update=True)
        self.graph.setMenuEnabled(enableMenu=False,enableViewBoxMenu=None)
        self.graph.setDownsampling(auto=True)
        self.curve=self.graph.plot()
        self.graph_umbral=pg.InfiniteLine(pen='b',angle=0,movable=True)
        self.graph.enableAutoRange('y', False)
        espacio_pg.setCentralItem(self.graph)
        plus_grid_fr.setCentralItem(self.tasas_bars)
        self.fft_n=0
        self.data_fft=0
        self.fft_l=0
        self.fft_aux=np.zeros([FFT_N,FFT_L/2])
        self.data_fft_aux=np.zeros([config.PAQ_USB*FFT_L_PAQ])
        self.graph.addItem(self.graph_umbral)
        self.graph_umbral.setValue(self.signal_config.thresholds[self.channel])
        self.pause_mode=False
        
        
    def update(self,data_handler,pause_mode):
        if pause_mode != self.pause_mode:
            if self.pause_mode == False:
                self.data_old=copy.copy(data_handler.graph_data)
                self.pause_mode=pause_mode
            else:
                self.pause_mode=pause_mode
        
        if self.pause_mode==True:
            data=self.data_old
        else:
            data=data_handler.graph_data
        
        n_view=data_handler.n_view
        xtime=data_handler.xtime
        
        self.signal_config.thresholds[self.channel]=self.graph_umbral.value()
        self.max_xtime=xtime[n_view-1]
        #tasas=np.zeros([4])
        
        #for i in range(4):
            #if self.tmode_auto[4*self.selec_tet+i] is True:
                #tasas[i]=calcular_tasa_disparo(x[i,:],umbral_calc[i])
                
            #else:       
                #tasas[i]=calcular_tasa_disparo(x[i,:],self.umbrales_manuales[4*self.selec_tet+i])
        
        #for i in range(4):
            #tasas[i]=calcular_tasa_disparo(data_new[i,:],self.umbrales_manuales[4*self.selec_tet+i])
        
        #if tasas[self.selec_canal] > 0 and self.beepbox.isChecked():
            ##print '\a' 
            #os.system("beep -f 700 -l 18 &")
        tet=int(self.channel/4)
        self.tasas_bars.update(data_handler.spikes_times[tet*4:tet*4+4])
        
        #self.curve.setPen(ch_colors[self.selec_canal])
        if self.mode is 0:
            #self.VB.setXRange(0, xtime[n_view-1], padding=0, update=False)
            self.curve.setPen(ch_colors[self.channel%4])
            self.curve.setData(x=xtime[:n_view],y=data[self.channel,:n_view])
        #elif self.mode is 1:  
            #self.curve.setPen(ch_colors[self.selec_canal])
            ##self.VB.setXRange(0, xtime[n_view-1], padding=0, update=False)
            #self.curve.setData(x=xtime[:n_view],y=x[self.selec_canal,:n_view], _callSync='off')
            #if self.tmode_auto[self.selec_canal+4*self.selec_tet] is True:
                #self.graph_umbral.setValue(umbral_calc[self.selec_canal])
            
        else:
            if( self.fft_l < FFT_L_PAQ):
                self.data_fft_aux[self.fft_l*config.PAQ_USB:(1+self.fft_l)*config.PAQ_USB]=data_handler.data_new[self.channel,:]
                self.fft_l+=1
            else:
                self.fft_l=0
                if (self.fft_n <FFT_N):
                    self.fft_aux[self.fft_n,:]=abs(fftpack.fft(self.data_fft_aux,n=FFT_L)[:FFT_L/2])** 2. / float(FFT_L)
                    self.fft_n+=1
                else:
                    self.fft_n=0
                    self.curve.setPen(ch_colors[self.channel%4])
                    self.curve.setData(x=fft_frec,y=np.mean(self.fft_aux,0))
                    
            #aux=fftpack.fft(data[self.selec_tet*4+self.selec_canal,:],n=FFT_L) #/config.CANT_DISPLAY
            #self.curve.setData(x=fft_frec,y=abs(aux[:np.size(aux)/2]))

    def change_display_mode(self,new_mode):
        
        if new_mode is 0:
            self.graph.addItem(self.graph_umbral)
            self.VB.setXRange(0, self.max_xtime, padding=0, update=False)
            #self.graph.setLogMode(x=False,y=False)
            
        #elif new_mode is 1:
            #self.graph.addItem(self.graph_umbral)
            #self.VB.setXRange(0, self.max_xtime, padding=0, update=False)
            ##self.VB.setXRange(0, self_max_xtime, padding=0, update=False)
            ##self.graph.setLogMode(x=False,y=False)
            
            self.graph_umbral.setValue(self.signal_config.thresholds[self.channel])
            #self.graph_umbral.setMovable(True)

        else: 
            #self.graph.setLogMode(x=True,y=True)
            self.VB.setXRange(0, config.FS/2, padding=0, update=False)
            if(self.mode is 0):
                self.graph.removeItem(self.graph_umbral)
            self.fft_l=0
            self.fft_n=0    
            #self.curve.setData(x=[0],y=[0])
        self.mode=new_mode
        
        
    def change_channel(self,canal):
        if int(self.channel/4) != int(self.channel/4):
            self.tasas_bars.tet_changed()
        self.channel=canal
        self.graph_umbral.setValue(self.signal_config.thresholds[self.channel])
        self.fft_l=0
        self.fft_n=0
        
    #def change_tmode(self,new_mode):
        #self.tmode_auto[self.channel]=(new_mode is 2)
        #self.change_line_mode()    


class  bar_graph(pg.PlotItem):
    def __init__(self):
        self.npack=0
        self.tasa_bars=list()
        self.tasas=np.zeros([PACK_xSPIKE_COUNT,4])
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

    def update(self,spike_times):  
            for i in range(4):
                #self.tasas[self.npack,i]=(spike_times[i][0]).size
                self.tasas[self.npack,i]=(np.greater(spike_times[i][0][1:]-spike_times[i][0][:-1],spike_duration_samples)).sum() + ((spike_times[i][0]).size > 0)
                tasas_aux=self.tasas[:,i].sum()/FREQFIX_xSPIKE_COUNT  
                    
                self.tasa_bars[i].setData(x=[i%4-0.3,i%4+0.3],y=[tasas_aux,tasas_aux], _callSync='off')
            self.npack+=1
            if self.npack is PACK_xSPIKE_COUNT:
               self.npack=0 

    def tet_changed(self):
        self.npack=0
        self.tasas=np.zeros([PACK_xSPIKE_COUNT,4])
        
class general_display():
    def __init__(self,espacio_pg,info_tet):
        layout_graphicos = pg.GraphicsLayout(border=(100,0,100)) #para ordenar los graphicos(items) asi como el simil con los widgets
        espacio_pg.setCentralItem(layout_graphicos)
        #self.vieboxs=list()
        self.set_canales=list() #canales seleccionados para ser mostrados
        self.curv_canal=list() #curvas para dsp actualizar los datos
        self.graphicos=list() #graphicos, para dsp poder modificar su autorange
        #graphicos principales
        
        
        if config.TWO_WINDOWS is False:
            main_win_ch=config.CANT_CANALES
    
        else:
            main_win_ch=int(config.CANT_CANALES*3/4/7)*4
            self.second_win=Second_Display_Window()            
            layout_graphicos_2=self.second_win.layout_graphicos
            self.second_win.show()
            
        for i in range(config.CANT_CANALES):
            vb=ViewBox_General_Display(i,info_tet)
            
            if (i < main_win_ch):
                graph = layout_graphicos.addPlot(viewBox=vb,row=int(i/4/ROWS_DISPLAY)*4+i%4, col=int(i/4)%ROWS_DISPLAY, rowspan=1, colspan=1)
            else:
                graph = layout_graphicos_2.addPlot(viewBox=vb,row=int((i-main_win_ch)/4/ROWS_DISPLAY)*4+(i-main_win_ch)%4, col=int((i-main_win_ch)/4)%ROWS_DISPLAY, rowspan=1, colspan=1)
            
            graph.hideButtons()
            graph.setDownsampling(auto=True)
            
            VB=graph.getViewBox()
            VB.setXRange(0, config.PAQ_USB, padding=0, update=True) #HARDCODE
            VB.setYRange(DISPLAY_LIMY,-DISPLAY_LIMY, padding=0, update=True)
            #self.vieboxs.append(VB)
            if i%4 is 0:
                graph.setTitle('Tetrodo ' + str(i/4+1))
            #if i%4 != 3:
                #graph.showAxis('bottom', show=False)
            graph.showAxis('bottom', show=False) 
            graph.showAxis('top', show=False)
            graph.showAxis('right', show=False)
            graph.showAxis('left', show=False)
            graph.showGrid(y=True)
            graph.setMenuEnabled(enableMenu=False,enableViewBoxMenu=False)
            graph.setMouseEnabled(x=False, y=False)
            self.curv_canal.append(graph.plot())
            self.curv_canal[-1].setPen(width=1,color=ch_colors[i%4])
            self.graphicos.append(graph)

        
        
    def change_Yrange(self,p):
        p=float(p)/10
        for i in range(config.CANT_CANALES):
           self.graphicos[i].setYRange(DISPLAY_LIMY*p,-1*DISPLAY_LIMY*p, padding=0, update=False)
    
    
    def changeXrange(self,i):
        max_x=i*config.PAQ_USB
        for i in range(config.CANT_CANALES):
            self.graphicos[i].setXRange(0,max_x, padding=0, update=False)
            
        
    def update(self,data,n_view):
        #self.casa+=1
        #step=config.PAQ_USB/float(config.FS)/4
        #if self.casa >= 4:
        #n=np.arange(n_view)
        for i in range(config.CANT_CANALES):
            self.curv_canal[i].setData(y=data[i,:n_view])
            #self.curv_canal[i].setData(x=n,y=data[i,:n_view])
                           
        #for i in range(config.CANT_CANALES):
           # self.vieboxs[i].setXRange(self.casa*step,(self.casa+1)*step, padding=0, update=False)
    #def setAutoRange(self,state):
        #for graphico in self.graphicos:
            #graphico.enableAutoRange('xy', state)  
    def close(self):
        if config.TWO_WINDOWS is True:
            self.second_win.Close()
            
class ViewBox_General_Display(pg.ViewBox):
    def __init__(self,i,info_tet):
        pg.ViewBox.__init__(self)
        self.i=i
        self.info_tet=info_tet
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.info_tet.change_channel(self.i)
    def mouseDragEvent(self,event):
        pass
          
class Second_Display_Window(QtGui.QDialog):
    ##Ventana extra
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi(second_win_file,self)
        self.setWindowFlags(QtCore.Qt.Window)
        self.layout_graphicos = pg.GraphicsLayout(border=(100,0,100)) #para ordenar los graphicos(items) asi como el simil con los widgets
        self.graphicsView.setCentralItem(self.layout_graphicos)
        self.closeable=False
    
    def Close(self):
        self.closeable=True
        self.close()
        
    def closeEvent(self, evnt):
        if self.closeable is False:
            evnt.ignore()
            
        
       
class  bci_data_handler():
    def __init__(self):
       
        #ojo aca!!!!1
        #self.graph_data=np.uint16(np.zeros([config.CANT_CANALES,config.CANT_DISPLAY]))
        #self.graph_data=np.uint16(np.zeros([config.CANT_CANALES,config.PAQ_USB])) 
        self.data_new=np.int16(np.zeros([config.CANT_CANALES,config.PAQ_USB]))
        self.spikes_times=0
        self.graph_data=np.int16(np.zeros([config.CANT_CANALES,config.MAX_PAQ_DISPLAY*config.PAQ_USB]))
        self.paqdisplay=0
        self.paq_view=1
        self.new_paq_view=1
        self.n_view=self.paq_view*config.PAQ_USB
        self.xtime=np.zeros([config.MAX_PAQ_DISPLAY*config.PAQ_USB])
        #self.xtime[:self.n_view]=np.linspace(0,config.MAX_PAQ_DISPLAY*config.PAQ_USB/float(config.FS),self.n_view)
        self.xtime[:self.n_view]=np.linspace(0,self.n_view/float(config.FS),self.n_view)
        ####
    
    def update(self,data_struct,is_filtered_signal):
        
        self.data_new=data_struct.new_data
        
        if data_struct.filter_mode is False:
            mean=self.data_new.mean(axis=1)
            self.data_new=self.data_new - mean[:, np.newaxis]
        self.spikes_times=data_struct.spikes_times
        if(self.new_paq_view != self.paq_view):
            self.paq_view=self.new_paq_view
            self.n_view=self.paq_view*config.PAQ_USB
            self.xtime[:self.n_view]=np.linspace(0,self.n_view/float(config.FS),self.n_view)
        
        if self.paqdisplay >= self.paq_view:
            self.paqdisplay=0
            
        for i in range(config.PAQ_USB):
            self.graph_data[:,self.paqdisplay*config.PAQ_USB+i]=self.data_new[:,i]
        self.paqdisplay+=1
        
    def change_paq_view(self,i):
        self.new_paq_view=i
        
        
        
def beep(sk_time):
    sk_time=sk_time[0]
    sk_size=np.size(sk_time)
    if not sk_size:
        return
    
    sp=(np.greater(sk_time[1:]-sk_time[:-1],spike_duration_samples)).sum()+1
    delay=int((one_pack_time*1000.0-spike_duration*sp)/sp)
    #os.system(beep_command + str(delay) + "-r" +str(sp))
    string=beep_command + str(delay)
    for i in range(sp):
		os.system(string)
    return
     
    
    #sk_time=np.reshape(sk_time,sk_size,1)
    #time.sleep(float(sk_time[0])/config.FS)

    #i=0
    #while i < sk_size:
            
        #x=sk_time[i]+spike_duration_samples
        #ii=0
        #while i+ii+1<sk_size and x>sk_time[i+ii+1]:
            #ii+=1
            #x=sk_time[i+ii]+spike_duration_samples
        #if ii is 0:
            #l=spike_duration
        #else:
            #l=int((sk_time[i+ii]-sk_time[i]+spike_duration_samples)*1000/config.FS)
        #os.system("beep -f" + BEEP_FREQ + "-l " + str(l))
        
        #if i+ii+1 < sk_size:
            #time.sleep(((sk_time[i+ii+1]-sk_time[i+ii]-spike_duration_samples)/config.FS))
        #i+=ii+1
    #return  
        
    #cadena_beep="beep -f" + BEEP_FREQ + "-l " + str(spike_duration)
    #time.sleep(float(sk_time[0])/config.FS) 
    #os.system(cadena_beep)
    
    #if sk_size is 1:
        #return
    #time.sleep(float(sk_time[1]-sk_time[0])/config.FS)   
    #sp_aux=(np.greater(sk_time[1:]-sk_time[:-1],spike_duration_samples))
    #sp=(sk_time[1:])[sp_aux]
    #if sk_size is 1:
        #return
    
    #time.sleep(float(sp[0]-sk_time[0])/config.FS) 
    
    #for i in range(sp.size-1):
        #t1=time.time()
        #os.system(cadena_beep)
        #aux=float(sp[i+1]-sp[i])/config.FS-(time.time()-t1)
        #if aux>0:
            #time.sleep(aux) 
        
    #os.system(cadena_beep)
    

class Config_processing():
    def __init__(self,filter_mode,thresholds):
        self.filter_mode=filter_mode
        self.thresholds=thresholds
