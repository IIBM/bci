#!/usr/bin/python
#configuracion

#CANT_CANALES=32+2
#LARGO_TRAMA=2*CANT_CANALES+2 #depende de la config del stella


CANT_CANALES=25
LARGO_TRAMA=2*CANT_CANALES
FS=float(20000)
PAQ_USB=8000
PAQ_DISPLAY=4
CANT_DISPLAY= PAQ_DISPLAY*PAQ_USB #minimo 
TIEMPO_DISPLAY=PAQ_USB/FS #minimo en ms.. 

FAKE_FILE=True #para file hay q cambiar el parser
MAX_SIZE_FILE=40*1024*1024
