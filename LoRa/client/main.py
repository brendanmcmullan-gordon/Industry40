import os
import socket
import time
import struct
import machine

from pysense import Pysense
from SI7006A20 import SI7006A20

from network import LoRa

# A basic package header
# B: 1 byte for the deviceId
# B: 1 bytes for the pkg size
# %ds - dynamically specifys the length of the string s in the format
_LORA_PKG_FORMAT = "BB%ds"

# A basic ack package
# B: 1 byte for the deviceId - replaced with last byte of 8 byte mac address -  DEVICE_ID = 0x01
# B: 1 byte for the pkg size
# B: 1 byte for the Ok (200) or error messages
_LORA_PKG_ACK_FORMAT = "BBB"

#set up sensor class
py = Pysense()
si = SI7006A20(py)

# Open a Lora Socket, use tx_iq to avoid listening to our own messages
# added australian frequency=916800000
#lora = LoRa(mode=LoRa.LORA, frequency=916800000, tx_iq=True)
lora = LoRa(mode=LoRa.LORA, frequency=922200000, tx_iq=True)
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
    msg = contentStr
    pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), device_addr, len(msg), msg)
    lora_sock.send(pkg)
        
    # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
    waiting_ack = True
    recvTimout = 0; # set a recieve timeout for 20 seconds
    while(waiting_ack and recvTimout < 20):
    # Since the maximum body size in the protocol is 255 the request is limited to 255 bytes
        recv_ack = lora_sock.recv(256)
        recvTimout = recvTimout + 1
        if (len(recv_ack) > 0):
            device_id, pkg_len, ack = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
            if (device_id == device_addr):  # if true packet ack is for this device
                if (ack == 200):
                    waiting_ack = False
                    print("ACK %s" %(device_id))    # print device id acknowledged should be its own address
                else:
                    waiting_ack = False
                    print("Message Failed")
        
        time.sleep(1) # added 1 second delay in loop for timeout
    time.sleep(10) # change this to a random time for multiple devices
