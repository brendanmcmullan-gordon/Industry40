import os
import time
import struct
import machine

from pysense import Pysense
from SI7006A20 import SI7006A20



#set up sensor class
py = Pysense()
si = SI7006A20(py)



while(True):
    # read sensors
    tempValue = si.temperature()        #/100.0
    humidityValue = si.humidity()  
    device_addr = 1
    contentStr='{ "H" : "%.2f", "T": "%.2f" }'%(humidityValue,tempValue)
    # ? change these to %d ? to reduce data size
    print("ID %s,  Data = %s" % (device_addr, contentStr))
    # Package send the JsoN contentStr containing temp and humidity value 

    time.sleep(3) # change this to a random time for multiple devices
