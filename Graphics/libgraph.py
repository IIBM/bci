# -*- coding: utf-8 -*-
"""
@author: Fernando J. Chaure
"""
from pyqtgraph.Qt import QtCore #interfaz en general
import pyqtgraph as pg #graphicos
import pyqtgraph.functions as fn
from PyQt4  import QtGui, uic
import numpy as np
from configuration import GENERAL_CONFIG as CONFIG
from threading import Thread
from copy import copy
from multiprocess_config import *
from collections import namedtuple
from configuration import BIO_CONFIG
from configuration import LIBGRAPH_CONFIG as LG_CONFIG
from configuration import FILE_CONFIG
from os import path, system
from spectral_view import SpectralHandler
from spike_sorting_view import SpikeSortingHandler
#import logging
#logging.basicConfig(format='%(levelname)s:%(message)s',filename='bci.log',level=logging.WARNING)

SPIKE_DURATION_SAMPLES = int(BIO_CONFIG['SPIKE_DURATION'] / 1000.0*CONFIG['FS'])
CH_COLORS = ['r', 'y', 'g', 'c', 'p', 'm'] * 3
NOT_SAVING_MESSAGE = 'without saving'
SAVING_MESSAGE = 'writing in:'


if int(CONFIG['FS'] / LG_CONFIG['FFT_RESOLUTION']) > int(LG_CONFIG['FFT_N'] * CONFIG['PAQ_USB'] / 2):
    FFT_SIZE = int(CONFIG['FS'] / LG_CONFIG['FFT_RESOLUTION'])
else:
    FFT_SIZE = int(LG_CONFIG['FFT_L_PAQ'] * CONFIG['PAQ_USB'] / 2)
    

#fft_frec = np.linspace(0, CONFIG['FS'] / 2, FFT_SIZE/2)
one_pack_time = CONFIG['PAQ_USB'] / CONFIG['FS']
PACK_xSPIKE_COUNT = int(np.ceil(float(LG_CONFIG['TIME_SPIKE_COUNT']) / one_pack_time))
FREQFIX_xSPIKE_COUNT = (float(PACK_xSPIKE_COUNT)*one_pack_time)
beep_command = "beep -f " + LG_CONFIG['BEEP_FREQ'] + " -l " \
                + str(BIO_CONFIG['SPIKE_DURATION']) + " -d "

UIFILE = path.join(path.abspath(path.dirname(__file__)), 'bciui.ui')

SHOW_ERROR_TIME = 5000 #ms

if LG_CONFIG['TWO_WINDOWS']:
    second_win_file = path.join(path.abspath(
                              path.dirname(__file__)),'second_window.ui')

UserChOptions_t = namedtuple('UserChOptions_t','conf_t filter_mode thr_values thr_manual_mode')

class MainWindow(QtGui.QMainWindow):
    channel_changed  = QtCore.pyqtSignal(int) 
    def __init__(self, processing_process, get_data_process):
        QtGui.QMainWindow.__init__(self)
        
        uic.loadUi(UIFILE, self)
        #self.tabifyDockWidget(self.firing_rates_dock,self.clustering_dock);
        self.showMaximized()
        
        self.SpS_dock.setVisible(False)
        self.actionSpS.setChecked(False)
        
        self.fft_dock.setVisible(False)
        self.actionFFT.setChecked(False)
        
        self.lfp_dock.setVisible(False)
        self.actionLFP.setChecked(False)
        
        self.neu_firing_rates_dock.setVisible(False)
        self.actionNeu_firing_rates.setChecked(False)
        
        self.show_group.setVisible(False)
        self.actionGroup_Viewer.setChecked(False)
        
        self.processing_process = processing_process
        self.get_data_process = get_data_process
        self.data_handler = bci_data_handler()
        self.signal_config = Channels_Configuration(queue = self.processing_process.ui_config_queue)#HARDCODE
        self.signal_config.try_send()
        
        self.channel_changed.connect(self.change_channel)
        
        self.spectral_handler = SpectralHandler(self, self.data_handler)
        self.spike_sorting_handler = SpikeSortingHandler(queue = self.processing_process.ui_config_queue, main_window = self)
        
        self.group_info = plus_display(self.data_handler, self.plus_grid, self.grid_group,
                                         self.plus_grid_fr, self.signal_config,
                                         self.thr_p,self.channel_changed)
        
        self.general_display = GeneralDisplay(self.data_handler, 
                                              self.espacio_pg, 
                                              self.channel_changed)
        
        
        ###Signal Slots Connections###

        QtCore.QObject.connect(self.display_scale, QtCore.SIGNAL("valueChanged(int)"),
                               self.general_display.changeYrange)  
        QtCore.QObject.connect(self.filter_mode_button, QtCore.SIGNAL("clicked( bool)"), 
                               self.change_filter_mode)  
        QtCore.QObject.connect(self.paq_view, QtCore.SIGNAL("valueChanged(int)"), 
                               self.changeXrange)                        
        QtCore.QObject.connect(self.active_channel_cb, QtCore.SIGNAL("clicked( bool)"),
                               self.activate_channel)
        QtCore.QObject.connect(self.manual_thr_cb, QtCore.SIGNAL("clicked( bool)"),
                               self.group_info.change_th_mode)
        QtCore.QObject.connect(self.thr_p, QtCore.SIGNAL("textEdited(const QString&)"),
                               self.group_info.thr_changed)
        QtCore.QObject.connect(self.pausa, QtCore.SIGNAL("clicked (bool)"),
                               self.group_info.set_pause)
                                
              
        self.thr_p.setValidator(QtGui.QDoubleValidator())
        self.contador_registro = -1
        self.timer = QtCore.QTimer()
        self.loss_data = 0
        self.timer.timeout.connect(self.update)
        
        self.timer.start(0) #si va demasiado lento deberia bajarse el tiempo
        get_data_process.process.start()
        processing_process.process.start()
        
        self.file_label = QtGui.QLabel("")
        self.statusBar.addPermanentWidget(self.file_label)
        #self.dockWidget.setTitleBarWidget(QtGui.QWidget())
        self.file_label.setText(NOT_SAVING_MESSAGE)
        self.change_filter_mode(self.filter_mode_button.isChecked())
        #self.elec_group = 0
        self.channel_changed.emit(0)
        
    def keyPressEvent(self, e):
    
        if e.key() == QtCore.Qt.Key_A and not e.isAutoRepeat():
            autoRange_state = self.group_info.VB.getState().get('autoRange')
            if autoRange_state.count(True) > 0:
                self.group_info.VB.disableAutoRange()
            else:
                self.group_info.VB.enableAutoRange()
        elif e.key() == QtCore.Qt.Key_P and not e.isAutoRepeat():
            self.pausa.click()
        
    def change_channel(self, channel):
        self.manual_thr_cb.setChecked(self.signal_config.th_manual_modes[channel])
        self.active_channel_cb.setChecked(self.signal_config.active_channels[channel])
        if LG_CONFIG['PROBE_CONF_L']:
            aux = '{}:{} | C:{}'.format(LG_CONFIG['PROBE_CONF_L'], 
        int(channel/CONFIG['ELEC_GROUP']) + 1, channel%CONFIG['ELEC_GROUP'] + 1)
            self.show_group.setWindowTitle('{} {}'.format(LG_CONFIG['GROUP_LABEL'],int(channel/CONFIG['ELEC_GROUP'])+ 1))
        else:
            aux = 'Electrode : {}'.format(channel+1)
            self.show_group.setWindowTitle(aux)
            
        self.info_label.setText(aux)
        self.show_s_channel.setWindowTitle(aux)
        #self.elec_group = channel%CONFIG['ELEC_GROUP']
        
    def about(self):
        QtGui.QMessageBox.about(self, "About",
        """Essentially, all expressions of human nature ever produced, from a caveman's paintings to Mozart's symphonies and Einstein's view of the universe, emerge from the same source: the relentless dynamic toil of large populations of interconnected neurons.
        Miguel Nicolelis""")  
     
     
    def change_filter_mode(self, mode):
        """"Define si se pide la segnial pura o la filtrada"""
        self.signal_config.change_filter_mode(mode)
        self.group_info.show_line = mode
        self.group_info.threshold_visible(mode)     

    def update(self):
        """"Loop que se ejecuta si llegan nuevos paquetes"""
        
        try:
            new_struct = self.processing_process.new_data_queue.get(TIMEOUT_GET)
        except Queue_Empty:
            return 1
        if new_struct['type'] == 'signal': 
            self.data_handler.update(new_struct)
            
            if self.beepbox.isChecked():
                t = Thread(target = beep,
                                     args = [self.data_handler.spikes_times[self.group_info.channel]])
                t.start()

            if (not self.get_data_process.warnings.empty()):
                new_mess = self.get_data_process.warnings.get(TIMEOUT_GET)       
                if new_mess[0] != SLOW_PROCESS_SIGNAL:
                    self.loss_data += new_mess[1]
                    self.statusBar.showMessage("Loss data: " + str(self.loss_data), SHOW_ERROR_TIME)
    
                else:
                    self.statusBar.showMessage(Errors_Messages[new_mess[0]], SHOW_ERROR_TIME)
            
            if (not self.processing_process.warnings.empty()):
                self.statusBar.showMessage(Errors_Messages[self.processing_process.warnings.get(TIMEOUT_GET)], SHOW_ERROR_TIME)
            
            self.spectral_handler.update()
            self.general_display.update()
            self.group_info.update()
            self.signal_config.try_send()

    
    def on_actionDetener(self):
        """detiene el guardado de datos"""
        self.get_data_process.control.send(STOP_SIGNAL)
        self.file_label.setText(NOT_SAVING_MESSAGE)

    def on_actionSalir(self):
        """Pide verificacion, detiene procesos y termina de guardar archivos"""
        if(QtGui.QMessageBox.question(
                        QtGui.QWidget(), 'Exit',
                        "Are you sure you want to exit the application?", 
                        QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, 
                        QtGui.QMessageBox.No) == QtGui.QMessageBox.No):                   
            return
        self.timer.stop()
        self.get_data_process.control.send(EXIT_SIGNAL)
        self.processing_process.control.send(EXIT_SIGNAL)
        self.get_data_process.process.join(2)
        self.processing_process.process.join(1)
        self.processing_process.process.terminate()
        self.get_data_process.process.terminate()
        self.general_display.close()
        #self.close()
        QtCore.QCoreApplication.instance().quit()
        #QtCore.QCoreApplication.instance().exit(N) devuelve N en APP.exec_()   
        import sys
        sys.exit()


    def on_actionNuevo(self):
        """Nuevo archivo de registro"""
        self.get_data_process.control.send(START_SIGNAL)
        self.contador_registro += 1
        self.file_label.setText(SAVING_MESSAGE + FILE_CONFIG['GENERIC_FILE'] +'-'+str(self.contador_registro))

    #def set_autoRange(self):
        #if self.autoRange.isChecked():
            #self.general_display.setAutoRange(True)
        #else:
            #self.general_display.setAutoRange(False)
    
        
    def closeEvent(self, event):
        u"""Redirige las senales que disparen ese evento al metodo on_actionSalir()"""
        event.ignore() 
        self.on_actionSalir()
        
    def changeXrange(self, i):
        """Modifica la cantidad de paquetes que se dibujan en los displays"""
        self.data_handler.change_paq_view(i)
        self.general_display.changeXrange(i)
    
    def activate_channel(self, i):
        """Agrega el canal seleccionado a la lista de canales activos"""
        self.signal_config.active_channels[self.group_info.channel] = i

       
    def on_actionStop_SP(self):
        """stop all spike sorting process"""
        pass
        #self.active_channel_cb.setCheckable(False)
        #self.processing_process.control.send(control_maker(self.active_channels))
        #implementacion pendiente
    #@QtCore.pyqtSlot()          
#    def view_firing_rate_dock(self,view):
#        self.firing_rates_dock.setVisible(view)  
                
class  plus_display():
    """Clase que engloba el display inferior junto a los metodos que lo implican individualmente"""  
    def __init__(self, data_handler, espacio_pg,grid_group, plus_grid_fr, signal_config, 
                 thr_p_label, channel_changed): 
        channel_changed.connect(self.change_channel)
        self.data_handler = data_handler
        self.channel = 0
        self.signal_config = signal_config
        self.tasas_bars = Bar_Graph()
        self.thr_p_label = thr_p_label
        #layout_graphicos.addItem(self.tasas_bars,row=None, col=0, rowspan=1, colspan=1)
        #graph=layout_graphicos.addPlot(row=None, col=1, rowspan=1, colspan=3)
        #create and configure selected channel plot:
        layout_tet= pg.GraphicsLayout()#border = (100, 0, 100)) 
        layout_tet.setSpacing(0)
        grid_group.setCentralItem(layout_tet)
        self.tet_curves = list()
        for i in range(CONFIG['ELEC_GROUP']):
            graph = layout_tet.addPlot(col=1,row = i+1,rowspan = 1, colspan = 1)
            axis = graph.getAxis('left')
            axis.setScale(scale = CONFIG['ADC_SCALE'])
            VB = graph.getViewBox()
            VB.setXRange(0, CONFIG['PAQ_USB']/float(CONFIG['FS']), padding=0, update=True)
            VB.setYRange(LG_CONFIG['DISPLAY_LIMY'], -LG_CONFIG['DISPLAY_LIMY'], padding=0, update=True)
            graph.setMenuEnabled(enableMenu = False, enableViewBoxMenu = None)
            graph.setDownsampling(auto = True)
            graph.showAxis('left', show = False)
            if i != CONFIG['ELEC_GROUP']-1:
                graph.showAxis('bottom', show = False) 
            self.tet_curves.append(graph.plot())
            if i==0:
                graph_0=graph
            else:
                graph.setYLink(graph_0)
                graph.setXLink(graph_0)
        #create and configure selected channel plot:
        self.graph = pg.PlotItem()
        axis = self.graph.getAxis('left')
        axis.setScale(scale = CONFIG['ADC_SCALE'])

        self.std = np.ndarray(CONFIG['#CHANNELS'])
        self.VB = self.graph.getViewBox()
        self.VB.setXRange(0, CONFIG['PAQ_USB']/float(CONFIG['FS']), padding=0, update=True)
        self.VB.setYRange(LG_CONFIG['DISPLAY_LIMY'], -LG_CONFIG['DISPLAY_LIMY'], padding=0, update=True)
        self.graph.setMenuEnabled(enableMenu = False, enableViewBoxMenu = None)
        self.graph.setDownsampling(auto = True)
        self.curve = self.graph.plot()
        #QtCore.QObject.connect(self.graph_thr, QtCore.SIGNAL("sigPositionChange()"), 
        self.graph.enableAutoRange('y', False)                       #self.pepe)
        espacio_pg.setCentralItem(self.graph)
        plus_grid_fr.setCentralItem(self.tasas_bars)
        
        #Create and onfigure ther line
        self.graph_thr = pg.InfiniteLine(pen = pg.mkPen('w', width=2), angle = 0, movable = True)
        self.graph_thr.sigPositionChangeFinished.connect(self.thr_changed)

        self.fft_n = 0
        self.fft_l = 0
        self.fft_aux = np.zeros([LG_CONFIG['FFT_N'], FFT_SIZE / 2+1])
        self.data_fft_aux = np.zeros([CONFIG['PAQ_USB']*LG_CONFIG['FFT_L_PAQ']])
        
        self.threshold_visible(True)
        self.graph_thr.setValue(self.signal_config.thresholds[self.channel])
        self.show_line = False
        self.pause_mode = False
        
        self.graph_thr.sigDragged.connect(self.moving_line)                     
        self.graph_thr.sigPositionChangeFinished.connect(self.free_line)           
        self.graph_thr_updatable = True          
    
    def moving_line(self):
        self.graph_thr_updatable = False
    
    def free_line(self):
        self.graph_thr_updatable = True
        
    def thr_changed(self, p = None):
        if self.signal_config.th_manual_modes[self.channel]:
            
            self.signal_config.change_th(self.channel, self.graph_thr.value())
            
            self.thr_p_label.setText("{0:.1f}".format(self.graph_thr.value()/self.std[self.channel]))
        else:
            
            if type(p)== pg.InfiniteLine:
                p = self.graph_thr.value() / self.std[self.channel]
                self.signal_config.change_th(self.channel, p)
                self.thr_p_label.setText("{0:.1f}".format(p))
            else:
                self.signal_config.change_th(self.channel, float(p))
                self.graph_thr.setValue(float(p)*self.std[self.channel])


    def set_pause(self, pause_mode):
        if pause_mode == True:
            self.data_old = copy(self.data_handler.graph_data)
        self.pause_mode = pause_mode

        
    def update(self):
        """Lo ejecutan al llegar nuevos paquetes"""

        if self.pause_mode == True:
            data = self.data_old
        else:
            data = self.data_handler.graph_data

        n_view = self.data_handler.n_view
        xtime = self.data_handler.xtime

        self.max_xtime = xtime[n_view-1]
        tet = int(self.channel / CONFIG['ELEC_GROUP'])

        self.tasas_bars.update(self.data_handler.spikes_times[tet*CONFIG['ELEC_GROUP']:tet*CONFIG['ELEC_GROUP']+CONFIG['ELEC_GROUP']])
        self.std = self.data_handler.std

        if self.signal_config.th_manual_modes[self.channel]:
            self.thr_p_label.setText("{0:.1f}".format(self.graph_thr.value()/self.std[self.channel]))

        if (not self.signal_config.th_manual_modes[self.channel]) and self.graph_thr_updatable:
            self.graph_thr.setValue(self.signal_config.thresholds[self.channel]*
            self.std[self.channel])


        self.curve.setPen(CH_COLORS[self.channel%CONFIG['ELEC_GROUP']])
        self.curve.setData(x = xtime[:n_view], y = data[self.channel, :n_view])
        
        fist_ch_group = int(self.channel/CONFIG['ELEC_GROUP'])*CONFIG['ELEC_GROUP']
        for i in range(CONFIG['ELEC_GROUP']):
            self.tet_curves[i].setPen(CH_COLORS[i])
            self.tet_curves[i].setData(x = xtime[:n_view], y = data[fist_ch_group+i, :n_view])      
             
    def threshold_visible(self, visible):
        """Define si el umbral es visible o no"""
        if visible:
            self.graph.addItem(self.graph_thr)
        else:
            self.graph.removeItem(self.graph_thr)
            
  
        
    def change_th_mode(self, manual):
         
        self.signal_config.change_th_mode(self.channel, manual)
        if manual:
            self.signal_config.change_th(self.channel, self.signal_config.thresholds[self.channel]*self.std[self.channel])
        else:
            self.signal_config.change_th(self.channel, self.signal_config.thresholds[self.channel] / self.std[self.channel])


    def change_channel(self, ch):
        """Modifica el canal que se grafica actualmente, 
        refrescando las barras de firing rate si pertenece a otro tetrodo"""
        #update plot
        if self.pause_mode == True:
            data = self.data_old
        else:
            data = self.data_handler.graph_data
        n_view = self.data_handler.n_view
        self.curve.setPen(CH_COLORS[ch%CONFIG['ELEC_GROUP']])
        self.curve.setData(x = self.data_handler.xtime[:n_view], y = data[ch, :n_view])
        
        fist_ch_group = int(ch/CONFIG['ELEC_GROUP'])*CONFIG['ELEC_GROUP']
        for i in range(CONFIG['ELEC_GROUP']):
            self.tet_curves[i].setPen(CH_COLORS[i])
            self.tet_curves[i].setData(x = self.data_handler.xtime[:n_view], y = data[fist_ch_group+i, :n_view])      
            
      
        if int(self.channel/CONFIG['ELEC_GROUP']) != int(ch/CONFIG['ELEC_GROUP']):
            self.tasas_bars.tet_changed()
        self.channel = ch
   
        if self.signal_config.th_manual_modes[self.channel]:
            self.graph_thr.setValue(self.signal_config.thresholds[self.channel])
            self.thr_p_label.setText("{0:.1f}".format(self.graph_thr.value()/self.std[self.channel]))
        else:
            self.graph_thr.setValue(self.signal_config.thresholds[self.channel]*
            self.std[self.channel])
            self.thr_p_label.setText("{0:.1f}".format(self.signal_config.thresholds[self.channel]))
            
        self.fft_l = 0
        self.fft_n = 0

class  Bar_Graph(pg.PlotItem):
    """Barras con tasas de disparo"""
    def __init__(self):
        self.npack = 0
        self.tasa_bars = list()
        self.tasas = np.zeros([PACK_xSPIKE_COUNT, CONFIG['ELEC_GROUP']])
        pg.PlotItem.__init__(self)
        self.showAxis('bottom', False)
        self.setMenuEnabled(enableMenu = False, enableViewBoxMenu = None)
        #self.showAxis('left', False)
        #self.enableAutoRange('y', False)
        self.setXRange(-0.4, (CONFIG['ELEC_GROUP']-1) + 0.4)
        self.enableAutoRange('x', False)
        self.setMouseEnabled(x=False, y=True)
        #self.hideButtons()
        
        for j in range(CONFIG['ELEC_GROUP']):
            self.tasa_bars.append(self.plot(pen = CH_COLORS[j],
                                            fillLevel=0,brush = pg.mkBrush(CH_COLORS[j])))


    def update(self, spike_times):  
        for i in xrange(len(spike_times)):
            self.tasas[self.npack, i] = (np.greater(spike_times[i][1:] - spike_times[i][:-1],
                                                    SPIKE_DURATION_SAMPLES)).sum() + ((spike_times[i]).size > 0)
            tasas_aux = self.tasas[:, i].sum() / FREQFIX_xSPIKE_COUNT  
            self.tasa_bars[i].setData(x = [i%CONFIG['ELEC_GROUP']-0.3, i%CONFIG['ELEC_GROUP']+0.3], 
                                   y = [tasas_aux,tasas_aux], _callSync='off')
            
        self.npack += 1
        if self.npack is PACK_xSPIKE_COUNT:
            self.npack = 0 

    def tet_changed(self):
        self.npack = 0
        self.tasas = np.zeros([PACK_xSPIKE_COUNT, CONFIG['ELEC_GROUP']])


class GeneralDisplay():
    def __init__(self, data_handler, espacio_pg, ch_changed_signal):
        self.data_handler = data_handler
        layout_graphicos = pg.GraphicsLayout(border = (100, 0, 100)) 
        #para ordenar los graphicos(items) asi como el simil con los widgets
        espacio_pg.setCentralItem(layout_graphicos)
        layout_graphicos.setSpacing(0)
        self.set_canales = list() #canales seleccionados para ser mostrados
        self.curv_canal = list() #curvas para dsp actualizar los datos
        self.graphicos = list() #graphicos, para dsp poder modificar su autorange
        #graphicos principales
                
        if LG_CONFIG['TWO_WINDOWS'] is False:
            main_win_ch = CONFIG['#CHANNELS']
    
        else:
            main_win_ch = int(CONFIG['#CHANNELS']*3/CONFIG['ELEC_GROUP']/7)*CONFIG['ELEC_GROUP']
            self.second_win = Second_Display_Window()            
            layout_graphicos_2 = self.second_win.layout_graphicos
            layout_graphicos_2.setSpacing(0)
            self.second_win.show()
            
        for i in xrange(0,CONFIG['#CHANNELS'],CONFIG['ELEC_GROUP']):

            if (i < main_win_ch):
                laxu = layout_graphicos.addLayout(row = int(i/CONFIG['ELEC_GROUP']/LG_CONFIG['COL_DISPLAY']), 
                                                    col = int(i/CONFIG['ELEC_GROUP'])%LG_CONFIG['COL_DISPLAY'], 
                                                rowspan = 1, colspan=1)#, border=(50,0,0)
                laxu.setSpacing(1)                        
            else:
                laxu = layout_graphicos_2.addLayout(row = int((i-main_win_ch)/CONFIG['ELEC_GROUP'] / LG_CONFIG['COL_DISPLAY']), 
                                                   col = int((i - main_win_ch)/CONFIG['ELEC_GROUP'])%LG_CONFIG['COL_DISPLAY'],
                                                    rowspan = 1, colspan=1)
                laxu.setSpacing(1)
                                                    
            
            label_aux=laxu.addLabel("<font size=\"3\">{} {}</font>".format(LG_CONFIG['GROUP_LABEL'], str(i / CONFIG['ELEC_GROUP'] + 1)), angle=-90, rowspan=CONFIG['ELEC_GROUP'])
            label_aux.setMaximumWidth(7)
            for j in xrange(i,min(i+CONFIG['ELEC_GROUP'],CONFIG['#CHANNELS'])):
                vb = ViewBox_General_Display(j, ch_changed_signal)
                graph = laxu.addPlot(viewBox = vb, col=1,
                                                     row = j%CONFIG['ELEC_GROUP'], 
                                                    rowspan = 1, colspan = 1)

                graph.hideButtons()
                graph.setDownsampling(auto = True)
                VB = graph.getViewBox()
                
                VB.setXRange(0, CONFIG['PAQ_USB'], padding = 0, update = True) #HARDCODE
                VB.setYRange(LG_CONFIG['DISPLAY_LIMY'], -LG_CONFIG['DISPLAY_LIMY'],
                             padding = 0, update = True)
    
                graph.showAxis('bottom', show = False) 
                graph.showAxis('top', show = False)
                graph.showAxis('right', show = False)
                graph.showAxis('left', show = False)
                graph.showGrid(y = True)
                graph.setMenuEnabled(enableMenu = False, enableViewBoxMenu = False)
                graph.setMouseEnabled(x = False, y = True)
                self.curv_canal.append(graph.plot())
                self.curv_canal[-1].setPen(width = 1, color = CH_COLORS[j%CONFIG['ELEC_GROUP']])
                self.graphicos.append(graph)

        
    def changeYrange(self, p):
        p = float(p) / 10
        for i in xrange(CONFIG['#CHANNELS']):
            self.graphicos[i].setYRange(LG_CONFIG['DISPLAY_LIMY'] * p, -1*LG_CONFIG['DISPLAY_LIMY']*p, padding=0, update=False)

    def changeXrange(self, i):
        max_x = i*CONFIG['PAQ_USB']
        for i in xrange(CONFIG['#CHANNELS']):
            self.graphicos[i].setXRange(0, max_x, padding = 0, update = False)
            
    def update(self):
        for i in xrange(CONFIG['#CHANNELS']):
            self.curv_canal[i].setData(y = self.data_handler.graph_data[i, :self.data_handler.n_view])
            
    def close(self):
        if LG_CONFIG['TWO_WINDOWS'] is True:
            self.second_win.Close()

class ViewBox_General_Display(pg.ViewBox):
    def __init__(self, i, ch_changed_signal):
        pg.ViewBox.__init__(self)
        self.i = i
        self.ch_changed_signal = ch_changed_signal
    
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.ch_changed_signal.emit(self.i)
            
    def mouseDragEvent(self, ev, axis = None):
        """If axis is specified, event will only affect that axis."""
        ev.accept()  ## we accept all buttons
        ## Ignore axes if mouse is disabled
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)
        mask = mouseEnabled.copy()
        if axis is not None:
            mask[1-axis] = 0.0

        ## Scale or translate based on mouse button
        if ev.button() & QtCore.Qt.RightButton:
            dif = ev.screenPos() - ev.lastScreenPos()
            tr = self.childGroup.transform()
            tr = fn.invertQTransform(tr)
            self.scaleBy(x = None, y = ((mask[1] * 0.02) + 1) ** dif.y(), center=(0, 0)) #here mu change
            self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
            

class Second_Display_Window(QtGui.QDialog):
    ##Ventana extra
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi(second_win_file, self)
        self.setWindowFlags(QtCore.Qt.Window)
        self.layout_graphicos = pg.GraphicsLayout(border=(100, 0, 100)) 
        #para ordenar los graphicos(items) asi como el simil con los widgets
        self.graphicsView.setCentralItem(self.layout_graphicos)
        self.closeable = False
    
    def Close(self):
        self.closeable = True
        self.close()
        
    def closeEvent(self, evnt):
        if self.closeable is False:
            evnt.ignore()


class  bci_data_handler():
    """Controla el alineado de datos, actualizaciones y configuracion 
    de entrada, agregando una capa de abstraccion al resto de los metodos"""

    def __init__(self):

        self.data_new = np.int16(np.zeros([CONFIG['#CHANNELS'], CONFIG['PAQ_USB']]))
        self.spikes_times = 0 
        self.graph_data = np.int32(np.zeros([CONFIG['#CHANNELS'],
                                             LG_CONFIG['MAX_PAQ_DISPLAY'] * CONFIG['PAQ_USB']]))
        self.paqdisplay = 0
        self.paq_view = 1
        self.new_paq_view = 1
        self.n_view = self.paq_view*CONFIG['PAQ_USB']
        self.xtime = np.zeros([LG_CONFIG['MAX_PAQ_DISPLAY']*CONFIG['PAQ_USB']])
        self.xtime[:self.n_view] = np.linspace(0, self.n_view / float(CONFIG['FS']), self.n_view)
        self.std = np.ndarray(CONFIG['#CHANNELS'])
        self.filter_mode = False
    
    def update(self, data_struct):
        
        self.filter_mode = data_struct["filter_mode"]
        
        if data_struct["filter_mode"] is False:
            #mean = data_struct["new_data"].mean(axis=1)
            self.data_new = data_struct["new_data"] #- mean[:, np.newaxis]
        else:
            self.data_new = data_struct["new_data"]
            
        self.spikes_times = data_struct["spikes_times"]
        self.std = data_struct["std"]
        
        if(self.new_paq_view != self.paq_view):
            self.paq_view = self.new_paq_view
            self.n_view = self.paq_view*CONFIG['PAQ_USB']
            self.xtime[:self.n_view] = np.linspace(0, self.n_view / float(CONFIG['FS']), 
                                                    self.n_view)
        
        if self.paqdisplay >= self.paq_view:
            self.paqdisplay = 0
        self.graph_data[:, self.paqdisplay*CONFIG['PAQ_USB']:(self.paqdisplay+1)*CONFIG['PAQ_USB']] = self.data_new
        self.paqdisplay += 1
        
    def change_paq_view(self, i):
        self.new_paq_view =  i
        
        
        
def beep(sk_time):
    if not np.size(sk_time):
        return
    sp = (np.greater(sk_time[1:] - sk_time[:-1], SPIKE_DURATION_SAMPLES)).sum() + 1
#    string = beep_command + str(
#        int((one_pack_time * 1000.0 - BIO_CONFIG['SPIKE_DURATION'] * sp) / sp))
#    for _ in xrange(sp):
#        system(string)
    string = beep_command + str(
        int((one_pack_time * 1000.0 - BIO_CONFIG['SPIKE_DURATION'] * sp) / sp)) + str(' -r ')+str(sp)
    system(string)
    return
    

class Channels_Configuration():
    def __init__(self, queue, filter_mode = None):
        
        self.th_manual_modes = np.zeros(CONFIG['#CHANNELS'],dtype=bool)
        self.thresholds = -4 * np.ones(CONFIG['#CHANNELS']) #all thresholds = -4*std()
        self.active_channels = [False] *CONFIG['#CHANNELS']
        self.filter_mode = filter_mode
        self.queue = queue
        self.changed = True
        
    def change_th(self, ch, value):
        if(self.thresholds[ch] != value):
            self.thresholds[ch] = value
            self.changed = True

    def change_th_mode(self, ch, value):
        self.th_manual_modes[ch] = value
        self.changed = True
            
    def change_filter_mode(self, state):
        self.filter_mode = state
        self.changed = True
        
    def try_send(self):
        if self.changed == True:
            try:
                self.queue.put(UserChOptions_t(conf_t = 'channels',filter_mode=self.filter_mode, 
                                             thr_values =self.thresholds,
                                             thr_manual_mode = self.th_manual_modes))
                self.changed = False                      
            except Queue_Full:
                pass
            
