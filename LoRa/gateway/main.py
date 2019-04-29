#// Author : Steve Gale 29/04/19
#// Modified : SG - 29/04/19 -
#// Copyright 2019 Steve Gale - seek permission and terms of use before you copy or modify this code
import socket
import struct
from network import LoRa

import json

# IP address of PHP / MySQL server
host = '192.168.88.233'
port = 80

#IP address of pycom device
print(wlan.ifconfig()[0] + ' connecting to '+ host)                  # check if Lopy DHCP IP has changed

postStr = 'POST /SipyRest/InsertSipyIOTjsonRESTData2.php HTTP/1.1\r\n'
hostStr = 'Host: %s:%s\r\n'%(str(host),str(port))
contentTypeStr = 'Content-Type: application/json\r\n'

# A basic package header
# B: 1 byte for the deviceId - recv_pkg[0]
# B: 1 byte for the pkg size - recv_pkg[1]
# %ds: Formated string for string  apprx 23 chars
_LORA_PKG_FORMAT = "!BB%ds"
# A basic ack package
# B: 1 byte for the deviceId - 
# B: 1 bytes for the pkg size 
# B: 1 byte for the Ok (200) or error messages 
_LORA_PKG_ACK_FORMAT = "BBB"

# Open a LoRa Socket, use rx_iq to avoid listening to our own messages, use australian frequency
#lora = LoRa(mode=LoRa.LORA, frequency=916800000,rx_iq=True)
# set to 922.2 MHz for Malaysia
lora = LoRa(mode=LoRa.LORA, frequency=916800000,rx_iq=True)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

while (True):
   # Since the maximum body size in the protocol is 255 the request is limited to 512 bytes
   recv_pkg = lora_sock.recv(512)

   # If at least a message with the header (2 byte) is recieved ,process it
   if (len(recv_pkg) > 2):
      recv_pkg_len = recv_pkg[1]

      # If message is corrupted do not continue to process
      try:
         # Unpack the message based on the package format (protocol definition)
         device_id, pkg_len, msg = struct.unpack(_LORA_PKG_FORMAT % recv_pkg_len, recv_pkg)

         #print('Device: %d - Pkg:  %s' % (device_id, msg))
         
         # extract measured values from recieved Json string from LoRa client message
         obJsMeasuredVals = json.loads(msg) 
         TemperatureStr = json.dumps(obJsMeasuredVals["T"])  # key for Temperature value in dictionary
         HumidityStr = json.dumps(obJsMeasuredVals["H"])     # key for Humidity value in dictionary
 
         # construct new json string with measured values inserted for server post
         contentStr='{ "DeviceName" : "%d", "Humidity" : %s, "Temperature": %s }'%(device_id,HumidityStr,TemperatureStr)
         print (contentStr)
         contentLengthStr = 'Content-Length: %s\r\n\r\n'%str(len(contentStr))
         
         # format HTTP post payload string for sending to the PHP / mySQL server
         payload =  postStr + hostStr+ contentTypeStr + contentLengthStr  + contentStr
         print(payload)
        
         # connect to php / database server, send the payload data and recieve the server response
         s = socket.socket(
         socket.AF_INET, socket.SOCK_STREAM)

         s.connect((host, port))
         s.send(payload.encode())
         svrResponse = s.recv(4096)
         print(svrResponse)   
         
         # extract the json string from the recieved data based on byte location (could use content length and trim off from end of string)
         strJsonResponse = ""
         for b in range(148,192):    # json string location in recieved data (148,192) - this may change
            strJsonResponse += chr(svrResponse[b])
         #print(strJsonResponse)
         
         # convert recieved json string to a python object (dictionary)
         obJsRecieved = json.loads(strJsonResponse)      #dictionary object
         print(json.dumps(obJsRecieved))
         #print(json.dumps(obJsRecieved["code"]))         #key for code value in dictionary
         #print(json.dumps(obJsRecieved["message"]))      # key for message value in dictionary

      except ValueError:
         print ("Buffer too small OR JSON Value error")
      # Respond to device with an acknowledge packet
      ack_pkg = struct.pack(_LORA_PKG_ACK_FORMAT, device_id, 1, 200)
      lora_sock.send(ack_pkg)       # ack response sent to lora client
 