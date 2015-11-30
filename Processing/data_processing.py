from scipy import signal #proc de segnales
import numpy as np #vectores, operaciones matematicas
from configuration import GENERAL_CONFIG as CONFIG
from multiprocess_config import *
from configuration import SIGNAL_PROCESSING_CONFIG as SP_CONFIG

if SP_CONFIG['BAND_PASS']:
    FILTER_FREQ = [float(SP_CONFIG['FMIN']*2)/CONFIG['FS'],
                   float(SP_CONFIG['FMAX']*2)/CONFIG['FS']]
else:
    FILTER_FREQ = [float(SP_CONFIG['FMIN']*2)/CONFIG['FS']]


FILTER_COEF = signal.firwin(SP_CONFIG['LENGTH_FILTER'], FILTER_FREQ, width=None, 
                          window= SP_CONFIG['WINDOW_TYPE'], pass_zero=False)

if  CONFIG['FILTERED']:
    EXTRA_SIGNAL = 0
else:
    EXTRA_SIGNAL = SP_CONFIG['LENGTH_FILTER']-1

N_STORAGE = 3 #cantidad de paq q se van a usar para calcular medianas etc


class Signal_Parameters():
    def __init__(self):

        self.std = np.ndarray(CONFIG['#CHANNELS'])
        self.std_fd = np.ndarray(CONFIG['#CHANNELS'])
        self.std4upd = 0
    
    def parcial_update(self,data): 
        self.std[self.std4upd] = (calc_std(data[self.std4upd,:],0) + self.std[self.std4upd]) /2.
        self.std_fd[self.std4upd] = (calc_std(np.diff(data[self.std4upd,:]),0)
                                        + self.std_fd[self.std4upd]) /2.
        self.std4upd +=1
        if self.std4upd == CONFIG['#CHANNELS']:
            self.std4upd = 0
            
            
    def update(self,data): 
        self.std= calc_std(data,1)
        self.std= calc_std(np.diff(data),1)
        #next time wil execute the parcial_update method                    
        self.update = self.parcial_update   
        
#def calcular_umbral_disparo(data,canales):
    #x=abs(signal.lfilter(b_spike,a_spike,data[canales,:]))
    #umbrales=4*np.median(x/0.6745)
    #return x,umbrales
    
def firfilter(b,data):
    blen=len(b)
    new_data = b[0]*data[:,blen:]
    for i in xrange(1,blen):
        new_data += b[i]*data[:,blen-i:-i]
    return new_data
    
    
def calc_std(x,axis):
    return np.median(np.abs(x)/0.6745,axis)
    
def spikes_detect(x, umbral):  
    new_spikes_times = list()
    #aux=[]
    for i in xrange(CONFIG['#CHANNELS']):
        if(umbral[i]>0):
            aux = np.less(x[i,:],umbral[i])
        else:
            aux = np.greater(x[i,:],umbral[i])
        new_spikes_times.append(np.nonzero(aux[1:].__and__(~aux[:-1]))[0])  
        
    
    return new_spikes_times
    
def data_processing(data_queue, ui_config_queue, graph_data_queue,
                    proccesing_control, warnings):
    #import config
    graph_data = {
        "type" : 'signal', 
        "new_data" : 0,
        "spikes_times" : np.zeros([0]),
        "filter_mode" : False,
        "std" : np.zeros(CONFIG['#CHANNELS'],np.int16)
    }
    activated_clustering = np.zeros(CONFIG['#CHANNELS'],bool)
    clustered_channel = np.zeros(CONFIG['#CHANNELS'],bool)
    activated_sps = np.zeros(CONFIG['#CHANNELS'])
    params = Signal_Parameters()
    
    control = None

    new_data = np.ndarray([CONFIG['#CHANNELS'],
                           CONFIG['PAQ_USB'] + EXTRA_SIGNAL],dtype=np.int16)
    
    while(control != EXIT_SIGNAL):
        while not proccesing_control.poll():
            while not ui_config_queue.empty():
            #if not ui_config_queue.empty():
                ui_configs = ui_config_queue.get(TIMEOUT_GET)
                if ui_configs[0] == 'channels':
                    ui_ch_config = ui_configs

            if not data_queue.empty():
                new_pure_data = data_queue.get(TIMEOUT_GET)   
                if isinstance(new_pure_data, list):
                    continue                
                new_data[:,EXTRA_SIGNAL:] = new_pure_data.channels
            else:
                continue

            #filtered_data = (signal.lfilter(FILTER_COEF, [1], new_data)[:,EXTRA_SIGNAL:]) #this support iir
            filtered_data = firfilter(FILTER_COEF,new_data) #this is a little more fast
            
            params.update(filtered_data)
            
            new_thr = ui_ch_config.thr_values*(~ui_ch_config.thr_manual_mode*params.std + ui_ch_config.thr_manual_mode)
            
            spikes_times = spikes_detect(filtered_data, new_thr)
                   
            graph_data["spikes_times"] = spikes_times
            graph_data["std"] = params.std
            
            graph_data["filter_mode"] = ui_ch_config.filter_mode
            
            if ui_ch_config.filter_mode is True:
                graph_data["new_data"] = filtered_data
            else:
                graph_data["new_data"] = new_data[:, EXTRA_SIGNAL:]
                
            try:
                graph_data_queue.put_nowait(graph_data)
            except Queue_Full:
                try :
                    warnings.put_nowait(SLOW_GRAPHICS_SIGNAL) 
                except Queue_Full:
                    pass
            #new_data[:,:EXTRA_SIGNAL] = new_data[:, -EXTRA_SIGNAL:]
            if  not CONFIG['FILTERED']:
                new_data[:, :EXTRA_SIGNAL] = new_data[:, -EXTRA_SIGNAL:]
        
        control = proccesing_control.recv()
        
        #falta la opcion iniciar sorting usando la pipe q hace q 
        #se cierre el proceso para transportar la info
