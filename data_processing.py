from scipy import signal #proc de segnales
import numpy as np #vectores, operaciones matematicas
from configuration import GENERAL_CONFIG as CONFIG
from multiprocess_config import *
from configuration import SIGNAL_PROCESSING_CONFIG as SP_CONFIG

if SP_CONFIG['BAND_PASS'] is True:
    FILTER_FREQ = [float(SP_CONFIG['FMIN']*2)/CONFIG['FS'],
                   float(SP_CONFIG['FMAX']*2)/CONFIG['FS']]
else:
    FILTER_FREQ = [float(SP_CONFIG['FMIN']*2)/CONFIG['FS']]


FILTER_COEF = signal.firwin(SP_CONFIG['LENGTH_FILTER'], FILTER_FREQ, width=None, 
                          window= SP_CONFIG['WINDOW_TYPE'], pass_zero=False)

EXTRA_SIGNAL=SP_CONFIG['LENGTH_FILTER']-1

#MEAN_L=5  #ESTO PODRIA PONERSE A BASE DE TIEMPO

#def calcular_umbral_disparo(data,canales):
    #x=abs(signal.lfilter(b_spike,a_spike,data[canales,:]))
    #umbrales=4*np.median(x/0.6745,1)
    #return x,umbrales
    
#def calcular_tasa_disparo(x,umbral):
    #t1=time.time()
    #if umbral >= 0:
        #pasa_umbral=(x>umbral)
    #else:
        #pasa_umbral=(x<umbral)
    #np.sum(pasa_umbral[:-1] * ~ pasa_umbral[1:])
    #print time.time()-t1

#def spikes_detect(x,umbral):
#    b=np.matrix(x*np.sign(umbral)>np.abs(umbral),np.int)        
#    b=np.diff(b,1,1)
#    aux=np.nonzero(b)
#    new_spikes_times=list([[] for i in range(CONFIG['CANT_CANALES'])])
#    for i in range(aux[0].size):
#        new_spikes_times[aux[0][0,i]].append(aux[1][0,i])
#    
#    return new_spikes_times
#    
def spikes_detect(x, umbral):
    new_spikes_times = list()
    #aux=[]
    for i in xrange(CONFIG['CANT_CANALES']):
        if(umbral[i]>0):
            aux = np.less(x[i,:],umbral[i])
        else:
            aux = np.greater(x[i,:],umbral[i])
        new_spikes_times.append(np.nonzero(aux[1:].__and__(~aux[:-1])))    
        
    
    return new_spikes_times
    
def data_processing(data_queue, ui_config_queue, graph_data_queue,
                    proccesing_control, warnings):
    #import config
    graph_data = Data_proc2ui()
    control = ''
#    mean_calc=np.int16(np.zeros([CONFIG['CANT_CANALES'],MEAN_L]))
#    mean_l=0
#    mean_aux=np.ndarray([CONFIG['CANT_CANALES'],1])
#    new_data = np.ndarray([CONFIG['CANT_CANALES'],
#                           CONFIG['PAQ_USB'] + EXTRA_SIGNAL])
    new_data = np.ndarray([CONFIG['CANT_CANALES'],
                           CONFIG['PAQ_USB'] + EXTRA_SIGNAL*2])                       
    while(control != EXIT_SIGNAL):
        while not proccesing_control.poll():
            if not ui_config_queue.empty():
                try:
                    ui_config = ui_config_queue.get(TIMEOUT_GET)
                except Queue_Empty:
                    pass
            
            try:
                new_pure_data = data_queue.get(TIMEOUT_GET) #UN DESASTRE!!!!!   
                new_data[:,EXTRA_SIGNAL*2:] = new_pure_data.channels
            except  Queue_Empty:
                continue
            except AttributeError: #no se porque, entre q no envia nada y empieza envia una lista(?) y pincha channels
                continue
            #filtar y enviar si filtro activo en conf o bien asi como esta
            #casa falta muucho 
#            new_data[:,CONFIG['LENGTH_FILTER']-1:]=new_data[:,CONFIG['LENGTH_FILTER']-1:]-mean_aux
            
            
            #filtered_data = signal.lfilter(FILTER_COEF, 1, new_data)[:,EXTRA_SIGNAL:] 
            #terriblemente mal no tiene en cuenta nada
            filtered_data=signal.filtfilt(FILTER_COEF, [1], new_data,padtype=None)[:,EXTRA_SIGNAL:-EXTRA_SIGNAL]
            spikes_times = spikes_detect(filtered_data, ui_config.thresholds)
            #casa ojo la fase lineal q desplaza todo
            

            graph_data.spikes_times = spikes_times
            
            if ui_config.filter_mode is True:
                graph_data.new_data = filtered_data
                graph_data.filter_mode = True
            else:
                graph_data.new_data = new_data[:, EXTRA_SIGNAL*2:]
                graph_data.filter_mode = False
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

       

class Data_proc2ui():
    def __init__(self):
        self.new_data = 0
        self.spikes_times = np.zeros([0])
        self.filter_mode = False
        #aca podria cambiar de filtro con un aviso para el recalculo.. 
        #aunq afectaria el sorting
