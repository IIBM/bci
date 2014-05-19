import ok
import time
import numpy

SERIALNUM = "1328000677"
BITFILENAME = 'fpga.bit'

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
bit100M = 7

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
 
    #print frec
    #print frecValueDic[str(frec)]
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
    if a & (0x0001<<bit4000k) :
      if (a & 0x000F) is not 0x000F :
        print "error1"
      return 4000000
    if a & (0x0001<<bit2000k) :
      if (a & 0x000F) is not 0x0007 :
        print "error2"
      return 2000000
    if a & (0x0001<<bit512k) :
      if (a & 0x000F) is not 0x0003 :
        print "error3"
      return 512000
    if a & (0x0001<<bit8k) :
      if (a & 0x000F) is not 0x0001 :
        print "error4"
      return 8000
    else:
      print "error5"
      return 0

  def data_count_available(self):
    self._xem.UpdateWireOuts()
    a = self._xem.GetWireOutValue(byteDataAvAddr)
    return a

  def read_data(self,size=m_u32SegmentSize):
    #datos = numpy.array([0 for i in range(size)],numpy.uint16)
    #if self.is_data_ready() == True and size<4000:
      datos = numpy.ndarray(size,numpy.uint16)
      n = self._xem.ReadFromPipeOut(byteDataOutAddr, datos)
      return datos,n
    #datos = numpy.ndarray(0,numpy.uint16)
    #return datos,0

  def read_block_data(self,size=m_u32SegmentSize):
    datos = numpy.ndarray(size,numpy.uint16)
    n = self._xem.ReadFromBlockPipeOut(byteDataOutAddr, 512,datos)
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
    a.start(10000)
    n = 0
    largo = 40
#    tramas = int(8000/largo)
    while n<50:

      while (a.is_data_ready() == False):
        time.sleep(.01)

      cant = 1000000
      n += 1
      ts = time.time()
      
#      l,b = a.read_data(cant)
      l,b = a.read_data(cant)
      print time.time() - ts
      print a.data_count_available()

      fb.write(l)
#      for i in range(b/2):
#        f.write(str(l[i]) + ' ')
#        if i % largo == largo -1:
#          f.write('\n')
    f.close()
    fb.close()
    a.close()
  except:
    print "error"
    f.close()
    fb.close()
    a.close()
