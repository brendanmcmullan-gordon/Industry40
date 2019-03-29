#// Author : Steve Gale 29/03/19
#// Modified : SG - 29/03/19 -
#// Copyright 2019 Steve Gale - seek permission and terms of use before you copy or modify this code
import socket
import json
import time

# IP address of PHP / MySQL server
host = '192.168.88.236'
port = 80

# check if Lopy DHCP IP has changed


for i in range(0,3):
    time.sleep(1)
    tempValue = 23.3        #/100.0
    humidityValue = 50
    try:
        # Test message  message based on the package format (protocol definition)
        device_id = 1
        msg = '{ "H" : "%.2f", "T": "%.2f" }'%(humidityValue,tempValue)
        print('Device: %d - Pkg:  %s' % (device_id, msg))
         
        # extract measured values from recieved Json string from LoRa client message
        obJsMeasuredVals = json.loads(msg) 
        TemperatureStr = json.dumps(obJsMeasuredVals["T"])  # key for Temperature value in dictionary
        HumidityStr = json.dumps(obJsMeasuredVals["H"])     # key for Humidity value in dictionary
 
        # construct new json string with measured values inserted for server post
        # construct json string with measured values insetred
        contentStr='{ "RoomName" : "E223", "Humidity" : "%.2f", "Temperature": "%.2f" }'%(humidityValue,tempValue)
        postStr = 'POST /i40Test/test/InsertJsonRESTData.php HTTP/1.1\r\n'
        hostStr = 'Host: %s:%s\r\n'%(str(host),str(port))
        contentTypeStr = 'Content-Type: application/json\r\n'
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

 