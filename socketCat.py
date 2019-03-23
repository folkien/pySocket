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

# Reading thread
def read():
    print "Output to ",args.outputFile,"."
    outFile = open(args.outputFile,'w')
    readedBytes=0;
    maxNoDataTime=5 #[s]
    readStartTime=time.time()
    lastDataTime=time.time()
    semaphoreStartSynchro.release()
    while ((readedBytes != inputSize) and ((time.time() - lastDataTime) < maxNoDataTime)):
        data = s.recv(256);
        if len(data) > 0:
            outFile.write(data)
            readedBytes+=len(data)
            lastDataTime=time.time()
            sys.stdout.write("\rReaded %d/%dB." % (readedBytes,inputSize))
            sys.stdout.flush()
        else:
            print "\nNo data time",(time.time() - lastDataTime),"s."
    outFile.close()
    print "\nWhole read transfer time:",(time.time()-readStartTime),"s."

# Writing thread
def main():
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

    # Wait on reading thread and close port
    tRead.join()
    print "Closed ",args.ipaddress," ",args.port
    s.close()

# Call main
main()
