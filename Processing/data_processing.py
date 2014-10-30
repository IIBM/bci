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

EXTRA_SIGNAL=SP_CONFIG['LENGTH_FILTER']-1


N_STORAGE = 3 #cantidad de paq q se van a usar para calcular medianas etc
DEFAULT_rT = 4 #for detect


class Signal_Parameters():
    def __init__(self, data):

        self.storage_channel = np.ndarray(CONFIG['PAQ_USB']*N_STORAGE)
        self.std = data.std(1)
        self.std_fd = np.diff(data).std(1)
        self.rT = DEFAULT_rT * np.ones(CONFIG['#CHANNELS'],np.int16)
    
    def update(self,ch):
        pass

#def calcular_umbral_disparo(data,canales):
    #x=abs(signal.lfilter(b_spike,a_spike,data[canales,:]))
    #umbrales=4*np.median(x/0.6745)
    #return x,umbrales
    
def calc_std(x):
    return np.median(np.abs(x)/0.6745,1)
    
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
        "new_data" : 0,
        "spikes_times" : np.zeros([0]),
        "filter_mode" : False,
        "std" : np.zeros(CONFIG['#CHANNELS'],np.int16)
    }

    
    
    
    control = ''
#    mean_calc=np.int16(np.zeros([CONFIG['CANT_CANALES'],MEAN_L]))
#    mean_l=0
#    mean_aux=np.ndarray([CONFIG['CANT_CANALES'],1])
#    new_data = np.ndarray([CONFIG['CANT_CANALES'],
#                           CONFIG['PAQ_USB'] + EXTRA_SIGNAL])
    new_data = np.ndarray([CONFIG['#CHANNELS'],
                           CONFIG['PAQ_USB'] + EXTRA_SIGNAL*2],dtype=np.int16)
    
    while(control != EXIT_SIGNAL):
        while not proccesing_control.poll():
            if not ui_config_queue.empty():
                try:
                    ui_config = ui_config_queue.get(TIMEOUT_GET)#usar algun tipo de estructura
                except Queue_Empty:
                    pass
            
            try:
                new_pure_data = data_queue.get(TIMEOUT_GET)   
                new_data[:,EXTRA_SIGNAL*2:] = new_pure_data.channels
            except  Queue_Empty:
                continue
            except AttributeError: #no se porque, entre q no envia nada y empieza envia una lista(?) y pincha channels
                continue
            #filtar y enviar si filtro activo en conf o bien asi como esta
            #falta muucho x implementar     
            
            #terriblemente mal no tiene en cuenta los bordes y la deteccion de spikes
            filtered_data = (signal.filtfilt(FILTER_COEF, [1], new_data,padtype=None)[:,EXTRA_SIGNAL:-EXTRA_SIGNAL])
            spikes_times = spikes_detect(filtered_data, ui_config[1]) 
            
            graph_data["spikes_times"] = spikes_times
            
            if ui_config[0] is True:
                graph_data["new_data"] = filtered_data
                graph_data["filter_mode"] = True
            else:
                graph_data["new_data"] = new_data[:, EXTRA_SIGNAL*2:]
                graph_data["filter_mode"] = False
            try:
                graph_data_queue.put_nowait(graph_data)
            except Queue_Full:
                try :
                    warnings.put_nowait(SLOW_GRAPHICS_SIGNAL) 
                except Queue_Full:
                    pass
            #new_data[:,:EXTRA_SIGNAL] = new_data[:, -EXTRA_SIGNAL:]
            new_data[:, :EXTRA_SIGNAL*2] = new_data[:, -2*EXTRA_SIGNAL:]
        control = proccesing_control.recv()
        #falta la opcion iniciar sorting usando la pipe q hace q 
        #se cierre el proceso para transportar la info
