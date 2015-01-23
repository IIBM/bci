# -*- coding: utf-8 -*-
"""

@author: Fernando J. Chaure
"""

#from configuration import SPECTRAL_CONFIG as S_CONFIG
from configuration import LIBGRAPH_CONFIG as S_CONFIG
import numpy as np
from scipy.signal import periodogram
from configuration import GENERAL_CONFIG as CONFIG
import pyqtgraph as pg
from PyQt4 import QtGui
CH_COLORS = ['r', 'y', 'g', 'c', 'p', 'm'] * 3


#Para no eliminar informacion al realizar una fft de menos muestras que la informacion que se utiliza para calcularla
if int(CONFIG['FS'] / S_CONFIG['FFT_RESOLUTION']) > int(S_CONFIG['FFT_N'] * CONFIG['PAQ_USB'] / 2):
    FFT_SIZE = int(CONFIG['FS'] / S_CONFIG['FFT_RESOLUTION'])
else:
    FFT_SIZE = int(S_CONFIG['FFT_L_PAQ'] * CONFIG['PAQ_USB'] / 2)

class S_segment():
    def __init__(self,label,minf,maxf):
        self.label = label
        self.maxf = maxf
        self.minf = minf
        
    def calc_S(self,fo,df,S):
        return np.sum(S[int((self.minf-fo)/df):int((self.maxf-fo)/df)+1])
    
S_SEGMENTS = list()
S_SEGMENTS.append( S_segment('Delta', 0,4))
S_SEGMENTS.append( S_segment('Theta' ,4,7))
S_SEGMENTS.append( S_segment('Alpha' ,8,15))
S_SEGMENTS.append( S_segment('Beta'  ,16,31))
S_SEGMENTS.append( S_segment('Gamma'  ,32, 70))
S_SEGMENTS.append( S_segment('Line', 49,51))


LFP_COLORS = [pg.intColor(i) for i in range(len(S_SEGMENTS))]




    
class SpectralHandler():
    def __init__(self, main_window,data_handler):
        self.data_handler = data_handler
        
        main_window.channel_changed.connect(self.change_channel)
        self.lfp_dock = main_window.lfp_dock
        self.fft_dock = main_window.fft_dock
        
        self.fft_n = 0
        self.fft_l = 0
        self.fft_aux = np.zeros([S_CONFIG['FFT_N'], FFT_SIZE / 2+1])
        self.data_fft_aux = np.zeros([CONFIG['PAQ_USB']*S_CONFIG['FFT_L_PAQ']])
        
        
        #Spectrum dock:
        self.Sgraph = pg.PlotItem()
        self.Sgraph.setMenuEnabled(enableMenu = False, enableViewBoxMenu = None)
        self.Sgraph.setDownsampling(auto = True)   
        self.Scurve = self.Sgraph.plot()
        self.Sgraph.enableAutoRange('y', False)
        axis = self.Sgraph.getAxis('left')
        axis.setScale(scale = CONFIG['ADC_SCALE']**2)
        self.Sgraph.setXRange(0,CONFIG['FS']/2)
        main_window.fft_grid.setCentralItem(self.Sgraph)
        
        
        #LFP dock:
        self.LFPgraph = pg.PlotItem()
        self.LFPgraph.setMenuEnabled(enableMenu = False, enableViewBoxMenu = None)
        self.barGraphItem = pg.BarGraphItem()

        
        self.x_lfp = np.arange(len(S_SEGMENTS))
        self.LFPbars = pg.BarGraphItem()
        self.LFPbars.setOpts(x=self.x_lfp, y0=0, y1=np.zeros_like(self.x_lfp), width=0.8)
        self.LFPgraph.addItem(self.LFPbars)
        self.seg_rel = np.ndarray([len(S_SEGMENTS)])
        
        self.LFPgraph.setXRange(0,len(S_SEGMENTS)+0.8)
        self.LFPgraph.setYRange(0,1)         
        ticks=list()
        for i in self.x_lfp:
            ticks.append(((i,S_SEGMENTS[i].label)))
        self.LFPgraph.getAxis('bottom').setTicks([ticks])
        self.LFPgraph.getAxis('bottom').tickFont=QtGui.QFont("System", 7)
        main_window.lfp_grid.setCentralItem(self.LFPgraph)
        
        
        
        
    def update(self):
        if self.lfp_dock.isVisible() or self.fft_dock.isVisible():
            
            if( self.fft_l < S_CONFIG['FFT_L_PAQ']):
                self.data_fft_aux[self.fft_l*CONFIG['PAQ_USB']:(1+self.fft_l)*CONFIG['PAQ_USB']] = self.data_handler.data_new[self.channel, :]
                self.fft_l += 1
            else:
                self.fft_l = 0
                if (self.fft_n < S_CONFIG['FFT_N']):
                    self.fft_frec,self.fft_aux[self.fft_n, :] = periodogram(self.data_fft_aux, fs=float(CONFIG['FS']),nfft = FFT_SIZE,scaling='spectrum')
                    self.fft_n += 1
                
                else:
                    self.fft_n = 0
                    spectrum = np.mean(self.fft_aux, 0)
                    if self.fft_dock.isVisible():
                        self.Scurve.setPen(CH_COLORS[self.channel%CONFIG['ELEC_GROUP']])
                        self.Scurve.setData(x = self.fft_frec, y = spectrum)
                    
                    if self.lfp_dock.isVisible():
                        fo = self.fft_frec[0]
                        df = self.fft_frec[1] - self.fft_frec[0]
                        for i in self.x_lfp:
                            self.seg_rel[i] = S_SEGMENTS[i].calc_S(fo,df,spectrum)

                        self.LFPbars.setOpts(x=self.x_lfp, width=0.8, y0=0, y1=self.seg_rel/spectrum.sum(), brushes=LFP_COLORS, pens=LFP_COLORS)
    
    
    def change_channel(self,ch): 
        if self.lfp_dock.isVisible() and ch!= self.channel:
            self.LFPbars.setOpts(x=self.x_lfp, y0=0, y1=np.zeros_like(self.x_lfp), width=0.8)
        
        
        self.channel = ch
        self.fft_l = 0
        self.fft_n = 0
       