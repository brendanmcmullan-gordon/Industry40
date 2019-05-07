'''

Author:     Industry 4.0 Python Collab Group
             -  Thaddeus Treloar

Version:    0.2
Phase:      Full python prototype

V0.2 Changes:

    -

'''

import threading, queue, socket

from json import loads, dumps
from datetime import datetime
from time import sleep
from struct import pack, unpack
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
    "SERVER_RESPONSE_LENGTH"          :  43
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

        return None, "Caught exception while sending: %s" % error

def parsePacket(clientPacket):

    clientPacketLength = clientPacket[1]

    try:

        deviceID, packetLength, packetBody = unpack(__SETTINGS('_LORA_PKG_FORMAT') % clientPacketLength, clientPacket)

        tempValue = loads(packetBody)["T"]
        humValue = loads(packetBody)["H"]
        c02Value = loads(packetBody)["C"]

        hostString = __SETTINGS["HOST_TEMPLATE"]%(__SETTINGS["DB_ADDRESS"],str(__SETTINGS["DB_PORT"]))
        packetLengthString = __SETTINGS["PACKET_LENGTH_TEMPLATE"]%str(len(packetLength))
        jsonString = __SETTINGS["JSON_TEMPLATE"]%(deviceID,tempValue,humValue,c02Value)

        fullPacket = __SETTINGS["POST_STRING"] + hostString + __SETTINGS["CONTENT_TYPE_STRING"] + packetLengthString + jsonString

        return fullPacket, deviceID, None

    except ValueError:

        return None, "Buffer too small or JSON key value error"

def listenClient(loraSocket):

    # Recieve packet until TimeoutError ocurrs
    try:
        clientPacket = loraSocket.recv(512)
    except Exception as error:
        return None, "Caught exception while listening: %s" % error

    if len(clientPacket) > 2:
        return clientPacket, None

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
    loraSocket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # socket set to Block mode. Change made from steve's code
    loraSocket.setblocking(True)

    # set socket timeout in case a client loses connectivity
    # part way through transmission
    loraSocket.settimeout(__SETTINGS["SOCKET_TIMEOUT"])

    return loraSocket

def retryPacket(sendFunction, functionArguments):
    for i in len(__SETTINGS["FAILED_PACKET_RETRY_LIMIT"]):

        sleep(__SETTINGS["FAILED_PACKET_RETRY_INTERVAL"])

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

def packetThreadWorker(threadListenStatus):

    loraSocket = createClientSocket()
    # listen for sensor packets
    clientPacket, listenErr = listenClient(loraSocket)

    # if there is an error listening, send a notification
    # to main thread and exit
    if listenErr != None:

        threadListenStatus(False)

            # Send log

        return

    else:

        # Send a notification of successful listen
        # to main thread so that second listen
        # thread can be started
        threadListenStatus.put(True)

        clientPacketParsed, clientId, errorMessage = parsePacket(clientPacket)

        # parse packet returns none if there has been an error parsing the client packet
        if clientPacketParsed[1] == None:

            '''
            LOG PACKET PARSING FAILURE
            '''

            return

        dbSocket = createServerSocket()

        serverResponse, serverError = sendServerPacket(clientPacketParsed, dbSocket)

        if serverError != None:

            serverResponse, serverError = retryPacket(sendServerPacket, {"dbPacket":clientPacketParsed, "dbSocket":dbSocket})

            if serverError != None:
                                          #failure code and message to send to client
                serverResponse = {"code": 1, "message": serverError}

                '''
                log db send failure
                '''

        response, ackError = sendClientAck(clientId, serverResponse["code"])

        if ackError != None:

            response, ackError = retryPacket(sendClientAck, {"loraSocket":loraSocket, "clientId":clientId, "responseCode":serverResponse})

            if ackError != None:
                '''
                log ack send failure
                '''

        '''
        log db entry success or failure
        '''
        #log successful db entry
        return


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
def main(): 
                # Ignore unused error until log implementation
    initStatus, initErr = init()

    threadListenStatus = queue.Queue()

    if initStatus == True:

        # create thread objects for listening and sending data packets
        packetThread1 = threading.Thread(name="listen1", target="packetThreadWorker", args=(threadListenStatus))
        packetThread2 = threading.Thread(name="listen2", target="packetThreadWorker", args=(threadListenStatus))
        packetThread3 = threading.Thread(name="listen1", target="packetThreadWorker", args=(threadListenStatus))
        packetThread4 = threading.Thread(name="listen2", target="packetThreadWorker", args=(threadListenStatus))

        while True:

            # check if the first listen thread is already running
            # if not, then run the thread and block until main
            # thread is notified that listening is successful or not
            if not packetThread1.isAlive():
                packetThread1.start()
                threadListenStatus.get()
                continue
            # check if the second listen thread is already running
            # if not, then run the thread and block until main
            # thread is notified that listening is successful or not
            elif not packetThread2.isAlive():
                packetThread2.start()
                threadListenStatus.get()
                continue
            # And the same continues for thread 3 and 4
            elif not packetThread3.isAlive():
                packetThread3.start()
                threadListenStatus.get()
                continue
            elif not packetThread4.isAlive():
                packetThread4.start()
                threadListenStatus.get()
                continue
            # as a fallback, this else will run if both threads
            # happen to be running at the same time.
            # If run, wait 2 secs before continuing the loop
            else:
                sleep(2)
                continue
    else:
        '''
        # need to add logging either files or
        log = open("/var/log/gateway/main.log", "w+")
        log.write(initErr)
        log.close()
        '''

        exit(1)

    exit(0)
