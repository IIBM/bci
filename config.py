#!/usr/bin/python
#General configuration

from os.path import isfile

if isfile("user_config_EXAMPLE.py"):
    from user_config_EXAMPLE import *
else:
    from user_config_DEFAULT import *

PAQ_DISPLAY=1
CANT_DISPLAY= PAQ_DISPLAY*PAQ_USB #minimo
MAX_PAQ_DISPLAY=8
TIEMPO_DISPLAY=PAQ_USB/FS #minimo en ms.. 

#esto podria ir aparte en conf file
MAX_SIZE_FILE=40*2**20 #40MB
#falta archivo de conf de hardware

