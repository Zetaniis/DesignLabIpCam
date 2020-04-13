#######################################################################################
#ONLY PYTHON LIBRARIES ARE NEEDED FOR SERVER
import select
import socket
from threading import Thread
import time
import serial
import cv2
import numpy as np

#######################################################################################
#Thred function resposible for handling new connection; It send the frame data from camera and forwards movement data from client to arduino
class ClientThread(Thread):

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print("New thread started for "+str(ip))

    def run(self):
        #Serial initialization to communicate with arduino
        ser = serial.Serial('COM3', baudrate=9600, timeout=1)
        time.sleep(3)
        while True:
            #Reading a single frame from camera
            ret, frame = cap.read()
            if ret == True:
                for sock in read_sockets:
                    #Flattening the frame data array and conversion to bytes
                    d = frame.flatten()
                    s = bytes(d)
                    #Sending charcteristic byte data combination that keeps the synchronization between the server and client
                    serverSock.sendto(b'\x01\x01\x01\x01', self.ip)
                    time.sleep(0.0025)
                    #Sending single frame divided into 20 packets
                    for i in range(20):
                        time.sleep(0.0015)
                        serverSock.sendto(bytes([i]) + s[i * 46080:(i + 1) * 46080], self.ip)
            else:
                break

            #Recieving movement data from client and sending it through serial to arduino
            ready = select.select([serverSock], [], [], 0)
            if ready[0]:
                data, addr = serverSock.recvfrom(1024)
                #Decoding the byte data to string
                dataC = str(data, 'utf-8')

                #Sending approperiate data to arduino
                if (dataC=="TL"): ser.write(b'1')
                elif (dataC == "TM"): ser.write(b'2')
                elif (dataC == "TR"): ser.write(b'3')
                elif (dataC == "ML"): ser.write(b'4')
                elif (dataC == "MM"): ser.write(b'5')
                elif (dataC == "MR"): ser.write(b'6')
                elif (dataC == "BL"): ser.write(b'7')
                elif (dataC == "BM"): ser.write(b'8')
                elif (dataC == "BR"): ser.write(b'9')
                else: ser.write(b'0')

########################################################################
#SOCKET INITIALIZATION

UDP_IP_ADDRESS = "192.168.56.1"#"0.0.0.0"#
UDP_PORT_NO = 6789

#Datagram setup of a socket for transfering udp packets
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#Binding the socket to ip address and port
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

#Validation of creation of socket
read_sockets, write_sockets, error_sockets = select.select([serverSock], [], [])
#serverSock.setblocking(1)

##########################################################################
#CAMERA INITIALIZATION
#Binding the camera to variable cap
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if (cap.isOpened() == False):
  print("Unable to read camera feed")

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

##########################################################################
#THREAD INITIALIZATION
#Table keeping the threads
threads = []

##########################################################################
#MAIN
#The server runs infinitely accepting the incoming connections and forwarding them to threads
while True:
#    serverSock.listen(4)
    print("Waiting for incoming connections...")
    for sock in read_sockets:
        #Recieving the data from client
        data, addr = serverSock.recvfrom(1024)
        newthread = ClientThread(addr, UDP_PORT_NO)
        newthread.start()
        threads.append(newthread)

    for t in threads:
        t.join()