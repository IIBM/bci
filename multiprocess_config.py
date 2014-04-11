#!/usr/bin/python
#Configurations for process communications
import config



TIMEOUT_GET=int(config.PAQ_USB/config.FS)
TIMEOUT_PUT=int(config.PAQ_USB/config.FS)/10

#--------
GRAPH_DATA_BUFFER=15
DATA_BUFFER=15
WARNIGNS_BUFFER =10

#--------
EXIT_SIGNAL=0
STOP_SIGNAL=1
START_SIGNAL=2

SLOW_PROCESS_SIGNAL=3
SLOW_GRAPHICS_SIGNAL=4

#--------
Errors_Messages = {SLOW_PROCESS_SIGNAL: "Loss data, slow processing", 
SLOW_GRAPHICS_SIGNAL:'Loss data, slow graphics' }
