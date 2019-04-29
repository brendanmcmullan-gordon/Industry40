import os
import time
import struct
import machine

from pysense import Pysense
from SI7006A20 import SI7006A20



#set up sensor class
py = Pysense()
si = SI7006A20(py)

# Open a Lora Socket, use tx_iq to avoid listening to our own messages
# added australian frequency=916800000
#lora = LoRa(mode=LoRa.LORA, frequency=916800000, tx_iq=True)
lora = LoRa(mode=LoRa.LORA, frequency=916800000, tx_iq=True)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

# use last byte of 8 byte mac addres as device ID
macAddress = lora.mac()
device_addr = macAddress[7]

while(True):
    # read sensors
    tempValue = si.temperature()        #/100.0
    humidityValue = si.humidity()  
    contentStr='{ "H" : "%.2f", "T": "%.2f" }'%(humidityValue,tempValue)
    # ? change these to %d ? to reduce data size
    print("ID %s,  Data = %s" % (device_addr, contentStr))
    # Package send the JsoN contentStr containing temp and humidity values
     

    time.sleep(10) # change this to a random time for multiple devices
