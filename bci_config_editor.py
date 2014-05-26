#!/usr/bin/python

import configuration
from PyQt4  import QtGui,uic

uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')
        



fft_l=8192*2 #en funcion de resolucion deseada

file=open(user_config_file,'w')
config.write(file)
