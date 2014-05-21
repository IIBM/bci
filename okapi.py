import ok
import time
import numpy

SERIALNUM = "1328000677"
BITFILENAME = 'fpga.bit'

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
frecValueDic = {'1000':0x0000,'2500':0x0001<<2,'5000':0x0002<<2,'10000':0x0003<<2,'15000':0x0004<<2,'20000':0x0005<<2,'25000':0x006<<2,'30000':0x0007<<2}

# 000  1k
# 001  2.5k
# 010  5k
# 011  10k
# 100  15k
# 101  20k
# 110  25k
# 111  30k

byteControlOutAddr = 0x21
bitDatoDisponible = 0
mascbitDatoDisponible = 0x0001<<bitDatoDisponible
bit4k = 0
bit16k = 1
bit32k = 2
bit128k = 3
bit1M = 4
bit5M = 5
bit10M = 6
bit60M = 7

byteDataAvAddr = 0x22

byteDataOutAddr = 0xA0

class OpalKelly():

  def __init__(self):
    self._xem = ok.FrontPanel()
    self._xem.OpenBySerial(SERIALNUM)
    self._xem.LoadDefaultPLLConfiguration()
    self._xem.ConfigureFPGA(BITFILENAME)
    self._byteControlIn = 0
    self._frecValue = 0
    msg = ('Device idVendor = ' + str(SERIALNUM) + ' not found')
    # was it found?
    if self._xem.IsFrontPanelEnabled() is not True :
        raise ValueError(msg)

  def reset(self):
    self._byteControlIn =  mascbitReset
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()

  def start(self,frec=30000):
    self.reset()
    time.sleep(.1)

    self._byteControlIn =  self._byteControlIn & ~mascbitReset
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()
    time.sleep(.1)
 
    if not (str(frec) in frecValueDic) :
       raise 'frec not valid'
    self._byteControlIn = frecValueDic[str(frec)]
    self._byteControlIn =  self._byteControlIn | mascbitTriggerFrec
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()
    time.sleep(.1)
 
    self._byteControlIn =  self._byteControlIn & ~mascbitTriggerFrec
    self._xem.SetWireInValue(byteControlInAddr, self._byteControlIn)
    self._xem.UpdateWireIns()
    time.sleep(.1)

  def is_data_ready(self):
    self._xem.UpdateWireOuts()
    a = self._xem.GetWireOutValue(byteControlOutAddr) & mascbitDatoDisponible
    return (a==mascbitDatoDisponible)

  def data_available(self):
    self._xem.UpdateWireOuts()
    a = self._xem.GetWireOutValue(byteControlOutAddr)
    if a & (0x0001<<bit60M) :
      if (a & 0x00FF) is not 0x00FF :
        print "error0"
      return 60000000
    if a & (0x0001<<bit10M) :
      if (a & 0x00FF) is not 0x007F :
        print "error1"
      return 10000000
    if a & (0x0001<<bit5M) :
      if (a & 0x00FF) is not 0x003F :
        print "error2"
      return 5000000
    if a & (0x0001<<bit1M) :
      if (a & 0x00FF) is not 0x001F :
        print "error3"
      return 1000000
    if a & (0x0001<<bit128k) :
      if (a & 0x00FF) is not 0x000F :
        print "error4"
      return 128000
    if a & (0x0001<<bit32k) :
      if (a & 0x00FF) is not 0x0007 :
        print "error5"
      return 32000
    if a & (0x0001<<bit16k) :
      if (a & 0x00FF) is not 0x0003 :
        print "error6"
      return 16000
    if a & (0x0001<<bit4k) :
      if (a & 0x00FF) is not 0x0001 :
        print "error7"
      return 4000
    else:
      print "error8"
      return 0

  def data_count_available(self):
    self._xem.UpdateWireOuts()
    a = self._xem.GetWireOutValue(byteDataAvAddr)
    return a

  def read_data(self,datos):
    n = self._xem.ReadFromPipeOut(byteDataOutAddr, datos)
    return n
    

  def read_block_data(self,datos):
    n = self._xem.ReadFromBlockPipeOut(byteDataOutAddr, 1024,datos)
    return n

  def close(self):
    self.reset()
    self._xem.ResetFPGA()
      
      
if __name__ == '__main__':
  import sys
  try:
    l = numpy.ndarray(100000,numpy.int16)
    f = open('salida.txt','w')
    a = OpalKelly()
    a.reset()
    time.sleep(.1)
    a.start(10000)
    n = 0
    largo = 40
    while n<10:

      while (a.data_available() < 100000):
        time.sleep(.01)

      n += 1
      
      b = a.read_data(l)
      f.write(l)
    f.close()
    a.close()
  except:
    print sys.exc_info()[0]
    print sys.exc_info()[1]
    print sys.exc_info()[2]
    f.close()
    a.close()
