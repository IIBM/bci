#!/usr/bin/python
#configuracion

#CANT_CANALES=32+2
#LARGO_TRAMA=2*CANT_CANALES+2 #depende de la config del stella


CANT_CANALES=24
LARGO_TRAMA=2*CANT_CANALES+2
FS=float(20000)
PAQ_USB=5000
PAQ_DISPLAY=1

CANT_DISPLAY= PAQ_DISPLAY*PAQ_USB #minimo
MAX_PAQ_DISPLAY=8
TIEMPO_DISPLAY=PAQ_USB/FS #minimo en ms.. 

FAKE_FILE=True #para file hay q cambiar el parser
#ojo q esta cambiado el parser para leer archivos!!

MAX_SIZE_FILE=40*1024*1024
TIMEOUT_GET=10*int(PAQ_USB/FS)
#-----------------------------------------------
STOP_SIGNAL=1
START_SIGNAL=2
EXIT_SIGNAL=0
