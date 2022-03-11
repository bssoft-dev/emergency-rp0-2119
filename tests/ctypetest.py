import ctypes


c_lib = ctypes.CDLL("/home/pi/SmartBell1/src/libspiLED.so")

c_lib.spiLED_initDevice()
c_lib.spiLED_on(255,1,20)