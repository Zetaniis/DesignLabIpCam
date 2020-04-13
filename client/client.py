#######################################################################################
#PYTHON LIBRARIES
import socket
import select
import kivy
import base64
import cv2
import numpy as np
import time

#######################################################################################
#GRAPHICAL LIBRARIES OF KIVY

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from functools import partial
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from threading import Thread
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.graphics.context_instructions import PushMatrix
from kivy.graphics.context_instructions import PopMatrix
from kivy.graphics.context_instructions import Rotate

#######################################################################################
#THREAD FOR SENDING THE MOVEMENT DATA

class ClientThread(Thread):

    def __init__(self,ip,port, sock, message):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.message = message
        print("[+] New thread started for "+str(ip))

    def run(self):
        try:
            self.sock.sendto(bytes(self.message, 'utf-8'), (self.ip, self.port))
        except:
            pass

#######################################################################################
#USER INTERFACE CLASS

class Application(GridLayout):
    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)
        self.time = 0

        self.packetLength = 46080                       #Packet length determined for 20 packets containing  640x480 pixel frame

        self.sumData = []
        self.bimage = b''                               #Byte variables used for frame operations
        self.transfer = b''
        self.texData = b''
        self.tmp = b''

        self.threads = []                               #Used for threading

        self.image = ""

                                                        #IP adress container
        self.ip = [TextInput(multiline=False, font_size=12),
                   TextInput(multiline=False, font_size=12),
                   TextInput(multiline=False, font_size=12),
                   TextInput(multiline=False, font_size=12)]

        self.port = TextInput(multiline=False, font_size=12)                        #Port container
        self.password = TextInput(multiline=False, password=True, font_size=12)     #Password container

        self.UDP_IP_ADDRESS = "192.168.56.1"
        self.UDP_PORT_NO = 6789
        self.Message = "ip: " + self.ip[0].text + "." + self.ip[1].text + "." + self.ip[2].text + "." + self.ip[
            3].text + " port: " + self.port.text

        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)          #Socket initialization
        self.clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 921600)     #Socket options

        self.popupWindow = Popup(title="Enter ip, port and password to access.")    #Popup window initialization

        self.cols = 1

        self.texture = Texture.create(size=(640, 480), colorfmt='rgb')              #Texture for camera frames initalization
        self.texture.flip_vertical()
        self.data = b'\xff\x00\x00' * 320 * 480 + (b'\x00\xff\x00' * 320 * 480)
        self.texture.blit_buffer(self.data, colorfmt='bgr')
        self.img = Image(size=self.texture.size, texture=self.texture)
        self.cent = ScatterLayout(do_rotation=False, do_scale=False, do_translation_y=False, do_translation_x=False,)
        self.add_widget(self.cent)
        self.cent.rotation = 90
        self.cent.add_widget(self.img)

        self.buttonsLay = GridLayout()

        self.buttonsLay.cols = 3                                                    #3x4 buttons grid setup
        self.add_widget(self.buttonsLay)

        self.BtnTL = Button(background_normal="arrowUL.png", background_down="arrowULNeg.png", pos_hint={"x":0.3, "top":0.3})
        self.BtnTL.bind(on_release=partial(self.BTN, message="TL"))
        self.buttonsLay.add_widget(self.BtnTL)

        self.BtnT = Button(background_normal="arrowUp.png", background_down="arrowUpNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.BtnT.bind(on_release=partial(self.BTN, message="TM"))
        self.buttonsLay.add_widget(self.BtnT)

        self.BtnTR = Button(background_normal="arrowUR.png", background_down="arrowURNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.BtnTR.bind(on_release=partial(self.BTN, message="TR"))
        self.buttonsLay.add_widget(self.BtnTR)

        self.BtnL = Button(background_normal="arrowLeft.png", background_down="arrowLeftNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.BtnL.bind(on_release=partial(self.BTN, message="ML"))
        self.buttonsLay.add_widget(self.BtnL)

        self.Btn = Button(background_normal="arrowMiddle.png", background_down="arrowMiddleNeg.png", pos_hint={"x":0.3, "top":0.3})
        self.Btn.bind(on_release=partial(self.BTN, message="MM"))
        self.buttonsLay.add_widget(self.Btn)

        self.BtnR = Button(background_normal="arrowRight.png", background_down="arrowRightNeg.png", pos_hint={"x":0.3, "top":0.3})
        self.BtnR.bind(on_release=partial(self.BTN, message="MR"))
        self.buttonsLay.add_widget(self.BtnR)

        self.BtnBL = Button(background_normal="arrowDL.png", background_down="arrowDLNeg.png", pos_hint={"x":0.3, "top":0.3})
        self.BtnBL.bind(on_release=partial(self.BTN, message="BL"))
        self.buttonsLay.add_widget(self.BtnBL)

        self.BtnB = Button(background_normal="arrowDown.png", background_down="arrowDownNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.BtnB.bind(on_release=partial(self.BTN, message="BM"))
        self.buttonsLay.add_widget(self.BtnB)

        self.BtnBR = Button(background_normal="arrowDR.png", background_down="arrowDRNeg.png", pos_hint={"x":0.3, "top":0.3})
        self.BtnBR.bind(on_release=partial(self.BTN, message="BR"))
        self.buttonsLay.add_widget(self.BtnBR)

        self.popupBtn = Button(background_normal="connect.png",background_down="connectNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.popupBtn.bind(on_release=self.showPopup)
        self.buttonsLay.add_widget(self.popupBtn)

        self.popupBtn = Button(background_normal="screenshot.png",background_down="screenshotNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.popupBtn.bind(on_release= self.frameShot)
        self.buttonsLay.add_widget(self.popupBtn)

        self.popupBtn = Button(background_normal="rec.png",background_down="recNeg.png",pos_hint={"x":0.3, "top":0.3})
        self.popupBtn.bind(on_release=partial(self.BTN, message="MM"))
        self.buttonsLay.add_widget(self.popupBtn)

        self.initPopup(self)

    #Screenshot function with name generation in format of date and hour
    def frameShot(self, instance):
        self.dateRaw = time.ctime()
        self.date = ''
        for i in self.dateRaw:
            if not (i==':' or i==' '):
                self.date += i
            else:
                self.date += '_'
        self.texture.save(self.date + '.png', flipped=0)

    #Update function executing roughly every 50ms recieving streamed packets and updating camera screen
    def update(self, dt):

        #Force updating the the camera screen with additional widget
        self.texTmp = Texture.create(size=(1,1), colorfmt='rgb')
        self.dataTmp = b'\xff\xff\xff'
        self.texTmp.blit_buffer(self.dataTmp, colorfmt='bgr')
        self.imgTmp = Image(size=self.texTmp.size, texture=self.texTmp)
        self.add_widget(self.imgTmp)
        self.remove_widget(self.imgTmp)

        #Checking if there is a socket connection
        ready = select.select([self.clientSock], [], [], 0)

        if ready[0]:
            #Reciving the packets and merging the byte data into a frame
            for i in range(20):
                #try:
                self.bimage, addr = self.clientSock.recvfrom(self.packetLength + 1)
                self.tmp = self.bimage[:1]
                self.tmp = self.tmp.hex()
                self.tmp = int(self.tmp, 16)
                #Checking for charcteristic byte data combination that keeps the synchronization between the server and client
                if self.bimage == b'\x01\x01\x01\x01':
                    break
                #Merging the byte data
                self.sumData[self.tmp*self.packetLength:(self.tmp+1)*self.packetLength] = list(self.bimage[1:])

        #Adding the valid frame data into texture blit_buffer to show it on screen
        if len(self.sumData) >= self.packetLength*20:
            self.texData = b''
            self.texData += bytes(self.sumData)
            self.texture.blit_buffer(self.texData, colorfmt='bgr')



    #Function handling the connection data and sending the information abput connection to server
    def submitIP(self, instance):
        #Checking if the ip address and port are not null
        if self.ip[0].text != "" and self.ip[1].text != "" and self.ip[2].text != "" and self.ip[3].text != "":
            self.UDP_IP_ADDRESS = self.ip[0].text + "." + self.ip[1].text + "." + self.ip[2].text + "." + self.ip[
                3].text
        else:
            self.UDP_IP_ADDRESS = "192.168.56.1"
        if self.port.text != "":
            self.UDP_PORT_NO = int(self.port.text)
        else:
            self.UDP_PORT_NO = 6789
        #Appending new thread that send connection data to server
        newthread = ClientThread(self.UDP_IP_ADDRESS, self.UDP_PORT_NO, self.clientSock, "message from client")
        newthread.start()
        self.threads.append(newthread)
        #Closing the popup
        self.popupWindow.dismiss()


    #Function initalizing the popup window
    def initPopup(self, instance):
        #Structuring the interface and adding the labels and text fields
        content = GridLayout()
        content.cols = 1

        inside = GridLayout()
        content.add_widget(inside)
        inside.cols = 2

        labelIP = BoxLayout()
        labelIP.width = 70
        labelIP.size_hint_x = None
        labelIP.add_widget(
            Label(text="IP:"))
        inside.add_widget(labelIP)

        ipGrid = BoxLayout()
        inside.add_widget(ipGrid)

        for ipGrid.i in self.ip:
            tmp = AnchorLayout(anchor_x='center', anchor_y='center')
            ipGrid.add_widget(tmp)
            ipGrid.i.size_hint = (1, 0.45)

            tmp.add_widget(ipGrid.i)

        labelPort = BoxLayout()
        labelPort.width = 70
        labelPort.size_hint_x = None
        labelPort.add_widget(
            Label(text="Port:"))
        inside.add_widget(labelPort)

        tmp = AnchorLayout(anchor_x='center', anchor_y='center')
        inside.add_widget(tmp)
        self.port.size_hint = (0.5, 0.45)
        tmp.add_widget(self.port)

        labelPass = BoxLayout()
        labelPass.width = 70
        labelPass.size_hint_x = None
        labelPass.add_widget(
            Label(text="Password"))
        inside.add_widget(labelPass)

        tmp = AnchorLayout(anchor_x='center', anchor_y='center')
        inside.add_widget(tmp)
        self.password.size_hint = (1, 0.45)
        tmp.add_widget(self.password)

        #Adding submit button at the bottom of the popup window
        btnLay = AnchorLayout(anchor_x='center', anchor_y='center')
        btnLay.size_hint = (1, 0.2)
        content.add_widget(btnLay)
        btnLay.submitIPBtn = Button(text="Submit", font_size=0.025*720, size_hint=(0.4, 0.9))
        btnLay.submitIPBtn.bind(on_release=self.submitIP)
        btnLay.add_widget(btnLay.submitIPBtn)

        self.popupWindow = Popup(title="Enter ip, port and password to access.", content=content,
                                 size_hint=(0.8, 0.6))

    #Function opening the popup window
    def showPopup(self, instance):
        self.popupWindow.open()

    #Funcition sending movement data to server on a new thread
    def BTN(self, *args, message):
        newthread = ClientThread(self.UDP_IP_ADDRESS, self.UDP_PORT_NO, self.clientSock, message)
        newthread.start()
        self.threads.append(newthread)

#Initalization of application object
class MyApp(App):
    def build(self):
        return Application()


if __name__ == "__main__":
    MyApp().run()

