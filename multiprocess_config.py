#!/usr/bin/python
#Configurations for process communications
import config



TIMEOUT_GET=int(config.PAQ_USB/config.FS)
TIMEOUT_PUT=int(config.PAQ_USB/config.FS)/10

#--------
GRAPH_DATA_BUFFER=15
DATA_BUFFER=20
WARNIGNS_BUFFER =10

#--------
EXIT_SIGNAL=0
STOP_SIGNAL=1
START_SIGNAL=2

SLOW_PROCESS_SIGNAL=3
SLOW_GRAPHICS_SIGNAL=4
SLOW_CAPTURE_DATA=5
DATA_NONSYNCHRONIZED=6
DATA_CORRUPTION=7


#--------
Errors_Messages = {SLOW_PROCESS_SIGNAL: "Loss data in processing", 
SLOW_GRAPHICS_SIGNAL: 'Loss data in graphics',
SLOW_CAPTURE_DATA: 'Loss data in capture',
DATA_NONSYNCHRONIZED: 'data non-synchronized',
DATA_CORRUPTION: 'the data stream is corrupted'}

