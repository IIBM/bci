from multiprocessing import Process, Pipe,Queue
from data_processing import data_processing
from multiprocess_config import *
from configuration import general_config as config


def init_process(dev_usb):
        
    data_queue = Queue(maxsize=DATA_BUFFER)
    get_data_control, ui_get_data_control = Pipe(duplex = False)
    get_data_warnings = Queue(maxsize=WARNIGNS_BUFFER)
    
    if config.ONLINE_MODE == True:
        from capture import  get_data
        p_read_data = Process(target=get_data, args=(get_data_control,get_data_warnings,dev_usb,data_queue))

    else:
        from capture import get_data_from_file
        p_read_data = Process(target=get_data_from_file, args=(get_data_control,get_data_warnings,data_queue))
    
    get_data_process=Get_data_process_handle(p_read_data,get_data_warnings,ui_get_data_control)
             
    graph_data_queue = Queue(maxsize=GRAPH_DATA_BUFFER)
    ui_config= Queue(maxsize=1)
    procesing_control, ui_procesing_control = Pipe(duplex = False)
    procesing_warnings = Queue(maxsize=WARNIGNS_BUFFER)
    p_procesing = Process(target=data_processing, args=(data_queue,ui_config,graph_data_queue,procesing_control,procesing_warnings))
    
    processing_process=Processing_process_handle(p_procesing,ui_procesing_control,procesing_warnings,ui_config,graph_data_queue)
    
    return processing_process,get_data_process
    
    
    
    
        
        
class Processing_process_handle():
    def __init__(self,process,proccesing_control,proccesing_warnings,ui_config_queue,graph_data_queue):
        self.process=process
        self.control=proccesing_control
        self.warnings=proccesing_warnings
        self.ui_config_queue=ui_config_queue
        self.new_data_queue=graph_data_queue
        

class Get_data_process_handle():
    def __init__(self,process,get_data_warnings,get_data_control):   
        self.process=process
        self.warnings=get_data_warnings
        self.control=get_data_control
