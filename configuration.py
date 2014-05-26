#!/usr/bin/python
#Load onfiguration

import os
from ConfigParser import ConfigParser

USER_CONFIG_FILE=os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config.ini")

config=ConfigParser()


#de aca tiene q salir el config hecho y capaz una funcion para acceder a las secciones



if os.path.isfile(USER_CONFIG_FILE):
    file=open(USER_CONFIG_FILE,'r')
    config.read(file)
else:
    file=open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config_DEFAULT.ini"),'r')
    config.read(file)

file.close()
