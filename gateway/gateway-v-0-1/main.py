'''
Author:     Industry 4.0 Python Collab Group
             -  Thaddeus Treloar
Version:    0.1
Phase:      Full python prototype/psuedo code
'''

import threading, queue
from datetime import datetime

class failedPacketObject:

    def __init__(self, packet, timestamp, retry=0):

        self.packet = packet
        self.timestamp = timestamp
        self.retryAttempt = retry

    def __repr__(self):

        return [self.packet, self.timestamp, self.retryAttempt]
        
    def incrementRetry(self):

        self.retryAttempt += 1

    def timeSinceCreation(self):

        return datetime.now() - self.timestamp
    

global __SETTINGS
__SETTINGS = {
    "FAILED_PACKET_RETRY_INTERVAL"    :   60,
    "FAILED_PACKET_RETRY_LIMIT"       :   5,
    "LOG_DIR"                        :   "/var/log/gateway"
}

def sendPacket(packet):

    packetStatus = ""

    if packetStatus == False:
        return packetStatus

    else:
        return True

def parsePacket(input):

    packetJson = ""

    return packetJson

def listenClient():

    clientPacket = ""
    clientErr = ""

    if clientErr == "":
        return clientPacket, None

    else:
        return None, clientErr

def failedPacketQueueThreadWorker():

    failedPacketDB = []

    while True:

        currentFailedPacket = failedPacketQueue.get()

        sendErr = sendPacket(currentFailedPacket[1])

        if sendErr == False:

            failedPacketDB.append(failedPacketObject(currentFailedPacket[1], currentFailedPacket[0], 1))

            '''
            log send failure
            '''

        sendErr = None

        for i in failedPacketDB:

            if datetime.now() - i.timestamp > __SETTINGS["FAILED_PACKET_RETRY_INTERVAL"]:

                sendErr = sendPacket(i.packet)

                if sendErr == False:
                    i.incrementRetry()
                    
                    if i.retryAttempt >= 5:
                        failedPacketDB.remove(failedPacketDB.index(i))

                        '''
                        log dropped packet due to too many retry failures
                        '''
                else:

                    failedPacketDB.remove(failedPacketDB.index(i))
                    '''
                    log that packet was retryed successfully
                    '''
            else:
                continue
                

def listenThreadWorker():

    clientPacket, listenErr = listenClient()

    if listenErr == None:
        return 
    
    else:
        clientPacketJson = parsePacket(clientPacket)

        sendErr = sendPacket(clientPacketJson)

        if sendErr == False:
            failedPacketQueue.put((datetime.now(), clientPacketJson))

            '''
            log send failure
            '''

        else:

            '''
            log success
            '''

            return


def init():

    initErr = ""

    global failedPacketQueue
    failedPacketQueue = queue.Queue()
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

    if initStatus == True:

        threadList = []

        failedPacketThread = threading.Thread(name="failedPacket", target="failedPacketThreadWorker", args=None)
        threadList.append(failedPacketQueueThreadWorker)
        failedPacketThread.start()

        while True:

            listenThread1 = threading.Thread(name="listen1", target="listenThreadWorker", args=None)
            listenThread2 = threading.Thread(name="listen2", target="listenThreadWorker", args=None)
            listenThread3 = threading.Thread(name="listen3", target="listenThreadWorker", args=None)
            listenThread4 = threading.Thread(name="listen4", target="listenThreadWorker", args=None)

            threadList.append(listenThread1)
            threadList.append(listenThread2)
            threadList.append(listenThread3)
            threadList.append(listenThread4)

            listenThread1.start()
            listenThread2.start()
            listenThread3.start()
            listenThread4.start()

            listenThread1.join()
            listenThread2.join()
            listenThread3.join()
            listenThread4.join()

        failedPacketThread.join()

    else:
        '''
        # need to add logging either files or 
        log = open("/var/log/gateway/main.log", "w+")
        log.write(initErr)
        log.close()
        '''

        exit(1)
    
exit(0)