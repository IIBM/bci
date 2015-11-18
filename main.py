#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Archivo main
"""
from pyqtgraph.Qt import QtGui #interfaz en general


def main(APP):
    

    from configuration import GENERAL_CONFIG as CONFIG
    if CONFIG == None:
        import sys
        sys.exit()
    from multi_process import init_process
    from Graphics.libgraph import MainWindow
    if CONFIG['ONLINE_MODE'] is False:
        dev_usb = False
    else:
        from capture import connect
        while(True):
        #verifica usb, luego comienza captura si es correcto
            
            try:
                dev_usb = connect()
                break
            except:
                if(QtGui.QMessageBox.question(
                        QtGui.QWidget(), 'Error',
                        "error: USB device not found, try again?", 
                        QtGui.QMessageBox.Ok |QtGui.QMessageBox.Cancel, 
                        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel):                   
                    return

# ## ## ## ## ## ## ## ## ## ## #
    
    processing_process, get_data_process = init_process(dev_usb)
    #processing_process,get_data_process=init_process(" ",0)
# ## ## ## ## ## ## ## ## ## ## #   
    

    window = MainWindow(processing_process, get_data_process)
    window.show()
    #APP.setWindowIcon(QtGui.QIcon('Graphics/icon.png'))
    return APP.exec_()
    
if __name__ == '__main__':
       
    APP = QtGui.QApplication([])
    main(APP)
#    while main(APP):
#        pass
    
