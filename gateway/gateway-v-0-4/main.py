'''

Author:     Industry 4.0 Python Collab Group
             -  Thaddeus Treloar

Version:    0.3
Phase:      Full python prototype

Notes:  Asyncronous version of v0.2
        Added micropython compatible module names

'''

import asyncore

import usocket as socket
import uasyncio as asyncio
from ujson import loads, dumps
from utime import sleep
from ustruct import pack, unpack
from network import LoRa


global __SETTINGS
__SETTINGS = {
    "SOCKET_TIMEOUT"                  :   60,
    "FAILED_PACKET_RETRY_INTERVAL"    :   60,
    "FAILED_PACKET_RETRY_LIMIT"       :   5,
    "LOG_DIR"                         :   "/var/log/gateway",
    "DB_ADDRESS"                      :   "192.168.88.236",
    "DB_PORT"                         :   80,

    # A basic package header
    # B: 1 byte for the deviceId - recv_pkg[0]
    # B: 1 byte for the pkg size - recv_pkg[1]
    # %ds: Formated string for string  apprx 23 chars
    "LORA_PKG_FORMAT"                 :   "!BB%ds",
    # A basic ack package
    # B: 1 byte for the deviceId -
    # B: 1 bytes for the pkg size
    # B: 1 byte for the Ok (200) or error messages
    "LORA_PKG_ACK_FORMAT"             :   "BBB",

    "LOG_INIT_ERROR"                  :   "",
    "LOG_DB_WRITE_ERROR"              :   "",
    "LOG_GENERIC_ERROR"               :   "",
    "JSON_TEMPLATE"                   :   '{ "DeviceName" : "%d", "Temperature": %s, "Humidity" : %s, "C02" : %s }',
    "PACKET_LENGTH_TEMPLATE"          :   'Content-Length: %s\r\n\r\n',
    "POST_TEMPLATE"                   : 'POST /SipyRest/InsertSipyIOTjsonRESTData2.php HTTP/1.1\r\n',
    "HOST_STRING"                     : 'Host: %s:%s\r\n',
    "CONTENT_TYPE_STRING"             : 'Content-Type: application/json\r\n',
    # json string location in recieved data (148,192) - this may change
    "SERVER_RESPONSE_START"           :  148,
    "SERVER_RESPONSE_LENGTH"          :  43,    # Alter php directory to reflect error logging
    "ERROR_JSON_TEMPLATE"           :   { "Error" : "%s", "HostName" : "%s" },
    "ERROR_TEMPLATE"                  :   'POST /SipyRest/InsertSipyIOTjsonRESTData2.php HTTP/1.1\r\n" + \
        "Host: %s:%s\r\nContent-Type: application/json\r\nContent-Length: %s\r\n\r\n%s'
                                      # Alter content type to reflect error logging
}                                     


def sendServerPacket(functionArguments):

    try:
        # connect with the server, send the packet and wait for response
        functionArguments["dbSocket"].connect((__SETTINGS["DB_ADDRESS"], __SETTINGS["DB_PORT"]))
        functionArguments["dbSocket"].send(functionArguments["dbPacket"].encode())
        dbResponse = functionArguments["dbSocket"].recv(4096)

        print(dbResponse)

        # extract the json string from the recieved data based on byte location (could use content length and trim off from end of string)
        dbJsonResponse = dbResponse[__SETTINGS["SERVER_RESPONSE_START"]:__SETTINGS["SERVER_RESPONSE_LENGTH"]+1]

        # convert recieved json string to a python object (dictionary)
        dbJsonResponseDict = loads(dbJsonResponse)      #dictionary object

        return dbJsonResponseDict, None

    except Exception as error:

        return None, None, "Caught exception while sending: %s" % error

def parsePacket(clientPacket):

    clientPacketLength = clientPacket[1]

    try:

        deviceID, packetLength, packetBody = unpack(__SETTINGS('_LORA_PKG_FORMAT') % clientPacketLength, clientPacket)

        tempValue = loads(packetBody)["T"]
        humValue = loads(packetBody)["H"]
        c02Value = loads(packetBody)["C"]

        hostString = __SETTINGS["HOST_TEMPLATE"]%(__SETTINGS["DB_ADDRESS"],str(__SETTINGS["DB_PORT"]))
        
        jsonString = __SETTINGS["JSON_TEMPLATE"]%(deviceID,tempValue,humValue,c02Value)
        packetLengthString = __SETTINGS["PACKET_LENGTH_TEMPLATE"]%str(len(jsonString))

        fullPacket = __SETTINGS["POST_STRING"] + hostString + __SETTINGS["CONTENT_TYPE_STRING"] + packetLengthString + jsonString

        return fullPacket, deviceID, None

    except ValueError:

        return None, "Buffer too small or JSON key value error"

async def listenClient(loraSocket, asyncQueue):

    clientPacket = ""
    # Recieve packet until TimeoutError ocurrs
    while True:
        try:
            clientPacket = loraSocket.recv(512)

        except Exception as error:
            return None, "Caught exception while listening: %s" % error

        if len(clientPacket) > 2:
            return clientPacket, None

        await asyncio.sleep(60)

def sendClientAck(functionArguments):

    ackPacket = pack(__SETTINGS["LORA_PKG_ACK_FORMAT"], functionArguments["clientId"], 1, functionArguments["responseCode"])
    try:
        functionArguments["loraSocket"].send(ackPacket)
        return None, None
    except Exception as error:
        return None, "Caught exception while sending ack to client: %s" % error

def createServerSocket():

    # set up socket for the db server
    dbSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    dbSocket.settimeout(__SETTINGS["SOCKET_TIMEOUT"])

    return dbSocket

def createClientSocket():

    lora = LoRa(mode=LoRa.LORA, frequency=916800000,rx_iq=True)
    loraSocket = asyncore.create_socket(socket.AF_LORA, socket.SOCK_RAW)

    # socket set to Block mode. Change made from steve's code
    #set back to non blocking for async compatibility
    loraSocket.setblocking(False)

    # set socket timeout in case a client loses connectivity
    # part way through transmission
    loraSocket.settimeout(__SETTINGS["SOCKET_TIMEOUT"])

    return loraSocket

async def retryPacket(sendFunction, functionArguments):
    for i in len(__SETTINGS["FAILED_PACKET_RETRY_LIMIT"]):

        await asyncio.sleep(__SETTINGS["FAILED_PACKET_RETRY_INTERVAL"])

        response, errorMessage = sendFunction(functionArguments)

        if errorMessage != None:

            continue

        else:

            break
    # packet thread has reached maximum number of send attempts
    else:
        return None, errorMessage

    # packet thread was able to successfully send the packet
    return response, None

async def asyncPacketTask(asyncQueue):

    loraSocket = createClientSocket()

    while True:
        if asyncQueue.empty():
            await listenQueue.put(False)
            # listen for sensor packets
            await asyncio.sleep(1)
            await clientPacket, listenErr = listenClient(loraSocket, asyncQueue)
            break
        else:
            await asyncio.sleep(10)
            continue

    # if there is an error listening, send a notification
    # to main thread and exit
    if listenErr != None:

        await asyncQueue.get()
                                                                        #change to gateway hostname
        errorJsonBody = __SETTINGS["ERROR_JSON_TEMPLATE"] % (listenErr, "PyGateway")
        fullErrorPacket = __SETTINGS["ERROR_TEMPLATE"] % (__SETTINGS["DB_ADDRESS"], __SETTINGS["DB_PORT"], len(errorJsonBody), errorJsonBody)

        dbSocket = createServerSocket()
        sendServerPacket({"dbSocket": dbSocket, "dbPacket": fullErrorPacket})

        return

    else:

        # Send a notification of successful listen
        # to main thread so that second listen
        # thread can be started
        await asyncQueue.get()
        await asyncio.sleep(1)

        clientPacketParsed, clientId, errorMessage = parsePacket(clientPacket)

        # parse packet returns none if there has been an error parsing the client packet
        if clientPacketParsed == None:
                                                                               # Alter to reflect new gateway name
            errorJsonBody = __SETTINGS["ERROR_JSON_TEMPLATE"] % (errorMessage, "PyGateway")
            fullErrorPacket = __SETTINGS["ERROR_TEMPLATE"] % (__SETTINGS["DB_ADDRESS"], __SETTINGS["DB_PORT"], len(errorJsonBody), errorJsonBody)

            dbSocket = createServerSocket()
            sendServerPacket({"dbSocket": dbSocket, "dbPacket": fullErrorPacket})

            loraSocket.close()
            dbSocket.close()

            return

        dbSocket = createServerSocket()

        serverResponse, serverError = sendServerPacket({"dbPacket":clientPacketParsed, "dbSocket":dbSocket})

        if serverError != None:

            serverResponse, serverError = retryPacket(sendServerPacket, {"dbPacket":clientPacketParsed, "dbSocket":dbSocket})

            if serverError != None:
                                          #failure code and message to send to client
                serverResponse = {"code": 1, "message": serverError}
                                                                                  # Alter to reflect server name
                errorJsonBody = __SETTINGS["ERROR_JSON_TEMPLATE"] % (serverError, "ServerName")
                fullErrorPacket = __SETTINGS["ERROR_TEMPLATE"] % (__SETTINGS["DB_ADDRESS"], __SETTINGS["DB_PORT"], len(errorJsonBody), errorJsonBody)

                sendServerPacket({"dbSocket": dbSocket, "dbPacket": fullErrorPacket})

        response, ackError = sendClientAck({"loraSocket":loraSocket, "clientId":clientId, "responseCode":serverResponse["code"]})

        if ackError != None:

            response, ackError = retryPacket(sendClientAck, {"loraSocket":loraSocket, "clientId":clientId, "responseCode":serverResponse["code"]})

            if ackError != None:

                errorJsonBody = __SETTINGS["ERROR_JSON_TEMPLATE"] % (ackError, clientId)
                fullErrorPacket = __SETTINGS["ERROR_TEMPLATE"] % (__SETTINGS["DB_ADDRESS"], __SETTINGS["DB_PORT"], len(errorJsonBody), errorJsonBody)

                sendServerPacket({"dbSocket": dbSocket, "dbPacket": fullErrorPacket})

        if serverError != None:

            loraSocket.close()
            dbSocket.close()

            return

        else:

            '''
                Local success log? if not remove coniditionals and just close sockets and exit

            '''
            loraSocket.close()
            dbSocket.close()
        
            return

async def asyncPacketWorker(asyncQueue):

    while True:

        await mainLoop.create_task()


def init():

    initErr = ""
    # add initialisation of __SETTINGS

    try:

        f = open(__SETTINGS["LOG_DIR"] + "send-error.log", "r")
        f.close()
    
    except(FileNotFoundError):

        f = open(__SETTINGS["LOG_DIR"] + "send-error.log", "w")
        f.write("")
        f.close()

    if initErr == True:

        return False, initErr

    return True, None

# Main loop
async def main():
                # Ignore unused error until log implementation
    initStatus, initErr = init()

    asyncQueue = asyncio.Queue()

    if initStatus == True:

        while True:

            await asyncio.gather(*[asyncPacketWorker(asyncQueue) for x in range(__SETTINGS["FAILED_PACKET_RETRY_LIMIT"])])

    else:
        '''
        # need to add logging either files or
        log = open("/var/log/gateway/main.log", "w+")
        log.write(initErr)
        log.close()
        '''

        exit(1)

    exit(0)


global mainLoop
mainLoop = asyncio.get_event_loop()
mainLoop.run_until_complete(main())
mainLoop.close()