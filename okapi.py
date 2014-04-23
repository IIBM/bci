import ok
import time
import numpy

SERIALNUM = "1328000677"
BITFILENAME = 'test.bit'

m_u32SegmentSize = 4096

byteReset = 0x00
bitReset = 1
mascbitReset = 0x0001<<bitReset

byteDatoDisponible = 0x21
bitDatoDisponible = 0
mascbitDatoDisponible = 0x0001<<bitDatoDisponible

byteDatos = 0xA0

class OpalKelly():

  def __init__(self):
    self._xem = ok.FrontPanel()
    self._xem.OpenBySerial(SERIALNUM)
    self._xem.LoadDefaultPLLConfiguration()
    self._xem.ConfigureFPGA(BITFILENAME)
    msg = ('Device idVendor = ' + str(SERIALNUM) + ' not found')
    # was it found?
    if self._xem.IsFrontPanelEnabled() is not True :
        raise ValueError(msg)

  def reset(self):
    self._xem.SetWireInValue(byteReset, mascbitReset)
    self._xem.UpdateWireIns()

  def start(self):
    self._xem.SetWireInValue(byteReset, mascbitReset)
    #self._xem.SetWireInValue(0x03, 0x0719)
    self._xem.UpdateWireIns()
  
  def is_data_ready(self):
    self._xem.UpdateWireOuts()
    a = self._xem.GetWireOutValue(byteDatoDisponible) & mascbitDatoDisponible
    #print a
    return (a==mascbitDatoDisponible)

  def read_data(self,size=m_u32SegmentSize):
    #datos = numpy.array([0 for i in range(size)],numpy.uint16)
    datos =np.ndarray(size,np.uint16)
    n = self._xem.ReadFromPipeOut(byteDatos, datos)
    return datos,n

  def close(self):
    self._xem.ResetFPGA()
      
      
if __name__ == '__main__':
  f = open('salida.txt','w')
  a = OpalKelly()
  a.reset()
  time.sleep(.1)
  a.start()
  time.sleep(1)
  n = 0
  largo = 35*2
  tramas = int(8000/largo)
  while n<5000:
    while (a.is_data_ready() == False):
      time.sleep(.01)

    n += 1
    l,b = a.read_data(largo*tramas)
    f.write(l)
  f.close()
  a.close()
