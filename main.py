#!/usr/bin/python

from pyqtgraph.Qt import QtGui #interfaz en general
import time #hora local 
from libgraph import MainWindow

from multi_process import init_process
from configuration import general_config as config

def main():
    app = QtGui.QApplication([])
    
    if config.ONLINE_MODE is False:
        dev_usb=False
    else:
        from capture import connect
        while(True):
        #verifica usb, luego comienza captura si es correcto
            
            try:
                dev_usb = connect()
                break
            except:
                if(QtGui.QMessageBox.question(QtGui.QWidget(),'Error', "error: USB device not found, try again?", 
                QtGui.QMessageBox.Ok |QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel ):                   
                    return

# ## ## ## ## ## ## ## ## ## ## #
    generic_file=QtGui.QFileDialog.getSaveFileName()
    processing_process,get_data_process=init_process(generic_file,dev_usb)
    #processing_process,get_data_process=init_process(" ",0)
# ## ## ## ## ## ## ## ## ## ## #   
    

    window=MainWindow(processing_process,get_data_process,generic_file)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
