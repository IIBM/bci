#!/usr/bin/python

from pyqtgraph.Qt import QtGui #interfaz en general
import time #hora local 
from libgraph import MainWindow
from capture import connect
from multi_process import init_process
import config

def main():
    app = QtGui.QApplication([])
    
    if hasattr(config, 'FAKE_FILE') and config.FAKE_FILE is True:
        dev_usb=False
    else:
        while(True):
        #verifica usb, luego comienza captura si es correcto
            try:
                dev_usb = connect()
                break
            except:
                if(QtGui.QMessageBox.question(QtGui.QWidget(),'Error', "error: USB device not found, try again?", 
                QtGui.QMessageBox.Ok |QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel ):
                    exit()
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
