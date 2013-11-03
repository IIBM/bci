#!/usr/bin/python
#configuracion

#CANT_CANALES=32+2
#LARGO_TRAMA=2*CANT_CANALES+2 #depende de la config del stella


CANT_CANALES=25
LARGO_TRAMA=2*CANT_CANALES
FS=1000
PAQ_USB=1000
CANT_DISPLAY= 5*PAQ_USB #minimo 
TIEMPO_DISPLAY=PAQ_USB/FS #minimo en ms.. 

FAKE_FILE=True #para file hay q cambiar el parser
MAX_SIZE_FILE=40*1024*1024
