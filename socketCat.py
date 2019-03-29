#!/usr/bin/python2.7
import argparse, os, sys
import threading
import time
import socket

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=True, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=True, help="output file")
parser.add_argument("-p", "--port", type=int, required=True, help="Port")
parser.add_argument("-a", "--ipaddress", type=str, required=True, help="IP address")
args = parser.parse_args()

#Assert
if (not args.inputFile):
    print "No input"
    sys.exit(1)

#Assert
if (not args.outputFile):
    print "No output"
    sys.exit(1)

#Assert
if (not args.ipaddress):
    print "No device"
    sys.exit(1)

#Assert
if (not args.port):
    print "No port"
    sys.exit(1)


semaphoreStartSynchro = threading.Semaphore()

# Read input file size
inputSize = os.stat(args.inputFile).st_size

# Socket Open
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ipaddress, args.port))

# Variable with state of Rx Thread
RxThreadRunning=0
TxTransmitted=0

# Reading thread
def read():
    global RxThreadRunning
    global TxTransmitted
    print "Output to ",args.outputFile,"."
    outFile = open(args.outputFile,'w')
    readedBytes=0;
    maxNoDataTime=5 #[s]
    readStartTime=time.time()
    lastDataTime=time.time()
    RxThreadRunning=1
    semaphoreStartSynchro.release()
    while ((readedBytes != inputSize) and ((time.time() - lastDataTime) < maxNoDataTime)):
        data = s.recv(256);
        sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB." % (TxTransmitted,inputSize,readedBytes,inputSize))
        sys.stdout.flush()
        if len(data) > 0:
            outFile.write(data)
            readedBytes+=len(data)
            lastDataTime=time.time()
        else:
            print "\nNo data time",(time.time() - lastDataTime),"s."

    outFile.close()
    sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB." % (TxTransmitted,inputSize,readedBytes,inputSize))
    print "\nWhole read transfer time:",str(round((time.time()-readStartTime),2)),"s."
    RxThreadRunning=0
    print "Transfer speed ",str(round((readedBytes/(time.time()-readStartTime))/1024,2)),"kB/s."

# Writing thread
def main():
    global RxThreadRunning
    global TxTransmitted
    # Read thread creation
    semaphoreStartSynchro.acquire()
    tRead = threading.Thread(target=read, args=())
    tRead.start()

    # Wait on start synchronization semaphore
    semaphoreStartSynchro.acquire()

    # Open write file and send lines
    print "Input from ",args.inputFile,"."
    print "InputSize : ",inputSize,"Bytes."
    inFile = open(args.inputFile,'r')
    for line in inFile:
        s.send(line)
        TxTransmitted   += len(line)
        if (RxThreadRunning == 0):
            break;


    # Wait on reading thread and close port
    tRead.join()
    print "Closed ",args.ipaddress," ",args.port
    s.close()

# Call main
main()
