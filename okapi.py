import ok
import time
import numpy

SERIALNUM = "1328000677"
BITFILENAME = 'test10k.bit'

m_u32SegmentSize = 4096

byteControlInAddr = 0x00
bitReset = 0
mascbitReset = 0x0001<<bitReset

bitTriggerFrec = 1
mascbitTriggerFrec = 0x0001<<bitTriggerFrec

byteDataInAddr = 0x03

# 0x077D -> 1KS/s  (2.8MHz)
# 0x0719 -> 5KS/s  (14MHz)
# 0x0E19 -> 10KS/s (28MHz)
# 0x1519 -> 15KS/s (42MHz)
# 0x1C19 -> 20KS/s (56MHz)
# 0x2319 -> 25Ks/s (70MHz)     // Se llena la FIFO de tramas a partir de esta frecuencia
# 0x2A19 -> 30KS/s (84MHz)
frecValueDic = {'1k':0x077D,'5k':0x0719,'10k':0x0E19,'15k':0x1519,'20k':0x1C19,'25k':0x2319,'30k':0x2A19}

byteControlOutAddr = 0x21
bitDatoDisponible = 0
mascbitDatoDisponible = 0x0001<<bitDatoDisponible

byteDataOutAddr = 0xA0

class OpalKelly():

  def __init__(self):
    self._xem = ok.FrontPanel()
    self._xem.OpenBySerial(SERIALNUM)
    self._xem.LoadDefaultPLLConfiguration()
    self._xem.ConfigureFPGA(BITFILENAME)
    self._byteControlIn = 0
    self._frecValue = 0
#    self._byteDataIn = 0
    msg = ('Device idVendor = ' + str(SERIALNUM) + ' not found')
    # was it found?
    if self._xem.IsFrontPanelEnabled() is not True :
        raise ValueError(msg)

  def reset(self):
    self._byteControlIn =  self._byteControlIn | mascbitReset
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()

  def start(self):
    self.reset()
    time.sleep(.1)

    self._byteControlIn =  self._byteControlIn & ~mascbitReset
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()
    time.sleep(.1)
 
    self._frecValue = frecValueDic['10k']
    self._xem.SetWireInValue(byteDataInAddr, self._frecValue)
    self._xem.UpdateWireIns()
    time.sleep(.1)
 
    self._byteControlIn =  self._byteControlIn | mascbitTriggerFrec
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()
    time.sleep(.1)

  def is_data_ready(self):
    self._xem.UpdateWireOuts()
    a = self._xem.GetWireOutValue(byteControlOutAddr) & mascbitDatoDisponible
    return (a==mascbitDatoDisponible)

  def read_data(self,size=m_u32SegmentSize):
    #datos = numpy.array([0 for i in range(size)],numpy.uint16)
    datos = numpy.ndarray(size,numpy.uint16)
    n = self._xem.ReadFromPipeOut(byteDataOutAddr, datos)
    return datos,n

  def close(self):
    self.reset()
    self._xem.ResetFPGA()
      
      
if __name__ == '__main__':
  try:
    f = open('salida.txt','w')
    fb = open('salidab.txt','w')
    a = OpalKelly()
    a.reset()
    time.sleep(.1)
    a.start()
    time.sleep(1)
    n = 0
    largo = 40
    tramas = int(8000/largo)
    while n<1000:
      while (a.is_data_ready() == False):
        time.sleep(.01)

      n += 1
      l,b = a.read_data(largo*tramas)
      fb.write(l)
      for i in range(b/2):
        f.write(str(l[i]) + ' ')
        if i % largo == largo -1:
          f.write('\n')
    f.close()
    fb.close()
    a.close()
  except:
    f.close()
    fb.close()
    a.close()
