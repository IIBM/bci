#!/usr/bin/python


from PyQt4  import QtGui,uic
import os
from ConfigParser import ConfigParser

USER_CONFIG_FILE=os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config.ini")

config=ConfigParser()


#de aca tiene q salir el config hecho y capaz una funcion para acceder a las secciones



if os.path.isfile(USER_CONFIG_FILE):
    config.read(USER_CONFIG_FILE)
    
else:
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config_DEFAULT.ini"))

uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')

app = QtGui.QApplication([])   
config.set('FILE','generic_file',QtGui.QFileDialog.getSaveFileName())

config.write(USER_CONFIG_FILE)
