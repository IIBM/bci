from scipy import signal #proc de segnales
import numpy as np #vectores, operaciones matematicas
import time
import config

#[b_spike,a_spike]=signal.iirfilter(4,[float(300*2)/config.FS, float(6000*2)/config.FS], rp=None, rs=None, btype='band', analog=False, ftype='butter',output='ba')
filter_coef=signal.firwin(100, [float(300*2)/config.FS,float(3000*2)/config.FS], width=None, window='hamming', pass_zero=False)


MEAN_L=5  #ESTO PODRIA PONERSE A BASE DE TIEMPO

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

def spikes_detect(x,umbral):
    b=np.matrix(x*np.sign(umbral)>np.abs(umbral),np.int)        
    b=np.diff(b,1,1)
    aux=np.nonzero(b)
    new_spikes_times=list([[] for i in range(config.CANT_CANALES)])
    for i in range(aux[0].size):
        new_spikes_times[aux[0][0,i]].append(aux[1][0,i])
    
    return new_spikes_times

def data_processing(data_queue,ui_config_queue,graph_data_queue,proccesing_control,warnings):
    #import config
    graph_data=Data_proc2ui()
    control=''
    mean_calc=np.int16(np.zeros([config.CANT_CANALES,MEAN_L]))
    mean_l=0
    mean_aux=np.ndarray([config.CANT_CANALES,1])
    while(control != config.EXIT_SIGNAL):
        while not proccesing_control.poll():
            if not ui_config_queue.empty():
                try:
                    ui_config=ui_config_queue.get(config.TIMEOUT_GET)
                except:
                    pass
            try:
                new_data=data_queue.get(config.TIMEOUT_GET)
            except:
                continue
            new_data=new_data[:-1,:] #casa en este caso xq saco el 25 avo
            #filtar y enviar si filtro activo en conf o bien asi como esta
            np.mean(new_data,1,out=mean_calc[:,mean_l])
            mean_l+=1
            if mean_l is MEAN_L :
                mean_l=0
            
            np.mean(mean_calc,1,out=mean_aux)
            #casa falta muucho 
            new_data=new_data-mean_aux
            
            
            filtered_data=signal.lfilter(filter_coef,1,new_data) #casa terriblemente mal no tiene en cuenta nada
                
            spikes_times=spikes_detect(filtered_data,ui_config.thresholds)
            #casa ojo la fase lineal q desplaza todo
            

            graph_data.spikes_times=spikes_times
            
            if ui_config.filter_mode is True:
                graph_data.new_data=filtered_data
            else:
                graph_data.new_data=new_data
                
            try:
                graph_data_queue.put_nowait(graph_data)
            except:
                try:
                    warnings.put_nowait('Loss data in slow graphics') 
                except:
                    pass
                
        control=proccesing_control.recv()
       #numpy.where !!!
       

class Data_proc2ui():
    def __init__(self):
        self.new_data=0
        self.spikes_times=np.zeros([0])
        #aca podria cambiar de filtro con un aviso para el recalculo.. aunq afectaria el sorting
