#!/usr/bin/python


CANT_CANALES=32+2
LARGO_TRAMA=2*CANT_CANALES #depende de la config del stella

FS=15000
PAQ_USB=1000
CANT_DISPLAY= 3*PAQ_USB #minimo 
TIEMPO_DISPLAY=PAQ_USB/FS*1000 #minimo en ms.. 

FAKE=True
