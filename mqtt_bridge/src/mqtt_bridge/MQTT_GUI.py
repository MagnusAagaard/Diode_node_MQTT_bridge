#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QBoxLayout, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QMessageBox, QSizePolicy
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, QtGui

from apscheduler.schedulers.background import BackgroundScheduler

import paho.mqtt.client as mqtt
from six.moves import urllib
import time
import csv
from collections import deque
import rospy

robot_status = 1;               #initialize status as free
robot_currentRoom = "";         #no room has been granted the robot yet
robot_queue = deque(["room1","room2","room3"]);          #queue empty

#wifi_loop = True
#while wifi_loop:        #wait for wifi connection before running the script
#    try:
#        urllib.request.urlopen("http://google.com")
#        wifi_loop= False
#    except urllib.error.URLError as e:
#        print(e.reason)
#    time.sleep(2)       #try again after 5 seconds if no connection

def mqtt_server_node():
    # init node
    rospy.init_node('mqtt_server_node')
    print("started")
    # start MQTT loop
    app = QApplication(sys.argv)
    ex = Example()

    sys.exit(app.exec_())
    rospy.spin()

class Example(QWidget):
    global robot_currentRoom;

    def __init__(self):

        super(Example, self).__init__()
        self.initUI()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        #self.client.connect("172.20.10.12")
        self.client.connect("10.0.2.15")
        self.client.loop_start()
        self.sched = BackgroundScheduler()
        self.sched.add_job(self.publish_queue, 'interval', seconds=2)
        self.sched.start()
 
    def closeEvent(self, event):
 
        reply = QMessageBox.question(self, 'Quit',
                                     "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.client.disconnect()
            self.client.loop_stop()
            self.sched.shutdown()
        else:
            event.ignore()

    def on_disconnect(self, client, userdata, rc):        #if we disconnected, wait for wifi to get back up
        rospy.loginfo('MQTT2 disconnected')

    def on_connect(self, client, userdata, flags, rc):
        #print("Connected with result code "+str(rc));
        client.subscribe([("cancelTopic" ,1), ("requestRobot",1)]); #subscribe to topics
        #sendString = "{"+'"'+"data"+'"'+':'+'"'+"helloFrompyth"+'"'+"}"
        #print(sendString)
        #client.publish("echo2",sendString)

    def on_message(self, client, userdata, msg):
        message = str(msg.payload).split('"')[3]
        print(message)
        print("message recieved: "+msg.topic+" "+msg.payload);

        global robot_status;
        global robot_currentRoom;
        global robot_queue;
            
        if msg.topic == 'cancelTopic':         #Cancel is called - cancel can only be called from the button that has been granted the robot
            #with open ('/home/ubuntu/log.csv','a') as csvfile:
                #writer = csv.writer(csvfile)
                #now = time.strftime('%d-%m-%Y %H:%M:%S')
                #writer.writerow([now, message, 'cancel'])
            if robot_status == 2:       #check if status is 2 (robot granted to a room)
                self.next_room_func()
            else :
                print("Cancel was called, but status is not 2");
                
        elif msg.topic == 'requestRobot':
            #with open ('/home/ubuntu/log.csv','a') as csvfile:
                #writer = csv.writer(csvfile)
                #now = time.strftime('%d-%m-%Y %H:%M:%S')
                #writer.writerow([now, message, 'request'])
            if robot_status == 1:
                robot_status = 2                   #grant the robot
                robot_currentRoom = message;        #when a button requests the robot, the room ID for the button is the payload
                self.enable_arrived()
                self.cur_room.setText(robot_currentRoom)
                #client.publish("buttonsInTopic", "2"+robot_currentRoom);
                print("requestRobot and status was 1")
                self.print_queue()
                
            else :
                if robot_queue.count(message) == 0 :
                    if robot_currentRoom != message :
                        print("Adding: "+message+" to the queue");
                        robot_queue.append(message);
                        self.print_queue()
                    else :
                        print("Button already has room")
                else :
                    print("Button is already in queue..");

        else :
            print("The topic recieved was not one I had to react on");

    def next_room_func(self):
        #Magnus: Her skal current room cancel ved at sende en besked fra PI til Knap (arduinoen)
        global robot_currentRoom
        global robot_status
        self.enable_arrived()
        if len(robot_queue) > 0:            #if there is anyone in the queue, grant them the robot
            robot_status = 2
            robot_currentRoom = robot_queue.popleft()       #first in queue gets the robot
            self.cur_room.setText(robot_currentRoom)
            self.print_queue()
            #self.client.publish("buttonsInTopic", "2"+robot_currentRoom);
        else:
            print('robot is free')
            robot_status = 1
            robot_currentRoom = ""
            self.cur_room.setText("Parkering")
            self.next_room.setText("")
            #self.client.publish("buttonsInTopic", "1");
            self.disable_buttons()

    def arrived(self):
        #with open ('/home/ubuntu/log.csv','a') as csvfile:
                #writer = csv.writer(csvfile)
                #now = time.strftime('%d-%m-%Y %H:%M:%S')
                #writer.writerow([now, robot_currentRoom, 'arrived'])
        self.client.publish("robotArrivedTopic", robot_currentRoom)	#Husk at tilføj dette
        self.enable_next()

    def enable_arrived(self):
        self.arrivedButton.setEnabled(True)
        self.nextButton.setEnabled(False)

    def enable_next(self):
        self.arrivedButton.setEnabled(False)
        self.nextButton.setEnabled(True)

    def disable_buttons(self):
        self.arrivedButton.setEnabled(False)
        self.nextButton.setEnabled(False)

    def print_queue(self):
        print (robot_queue)
        robot_queueString = ""
        for i in range(1, len(robot_queue)):
            robot_queueString += robot_queue[i]+"\n"
        if len(robot_queue) > 0:
            self.queue.setText(robot_queueString)
            self.next_room.setText("{}".format(robot_queue[0]))
        if len(robot_queue) == 1:
            self.queue.setText("Ingen kø")
            self.next_room.setText("{}".format(robot_queue[0]))
        elif len(robot_queue) == 0:
            self.queue.setText("Ingen kø")
            self.next_room.setText("Parkering")

    def publish_queue(self):
        robot_qString = robot_currentRoom + ";"
        for i in range(0,len(robot_queue)):
            robot_qString += robot_queue[i]+";"
        sString = "{"+'"'+"data"+'"'+':'+'"'+robot_qString+'"'+"}"
        if robot_qString != ";":
            self.client.publish("statusTopic", sString)
        elif robot_qString == ";":
            self.client.publish("statusTopic", "{"+'"'+"data"+'"'+':'+'"'+"free;"+'"'+"}")
        
        
           
    def initUI(self):
        self.nextButton = QPushButton("Næste")
        self.nextButton.setStyleSheet("margin:10px; font-size: 25pt; font-family:  ;")
        self.nextButton.clicked.connect(self.next_room_func)
        
        self.arrivedButton = QPushButton("Robot ankommet")
        self.arrivedButton.setStyleSheet("margin:10px; font-size: 25pt; font-family:  ;")
        self.arrivedButton.clicked.connect(self.arrived)

        
        self.cur_room_label = QLabel('Gå til:', self)
        self.cur_room_label.setStyleSheet("margin:5px; font-size: 15pt; font-family:  ;")
        self.cur_room_label.setAlignment(QtCore.Qt.AlignLeft)
        
        self.cur_room = QLabel("Parkering", self)
        self.cur_room.setStyleSheet("color: black; background-color: white; margin:2px; border:2px solid rgb(125, 125, 125); font-size: 50pt; font-family:  ;")
        #self.cur_room.resize(200, 100)
        self.cur_room.setAlignment(QtCore.Qt.AlignCenter)

        self.next_room_label = QLabel('Næste rum:', self)
        self.next_room_label.setStyleSheet("margin:5px; font-size: 15pt; font-family:  ;")
        self.next_room_label.setAlignment(QtCore.Qt.AlignLeft)

        self.next_room = QLabel("Intet", self)
        self.next_room.setStyleSheet("color: black; background-color: white; margin:2px; border:2px solid rgb(125, 125, 125); font-size: 40pt; font-family:  ;")
        #self.next_room.resize(2000, 1000)
        self.next_room.setAlignment(QtCore.Qt.AlignCenter)

        self.queue_label = QLabel('Kø:', self)
        self.queue_label.setStyleSheet("margin:5px; font-size: 15pt; font-family:  ;")
        self.queue_label.setAlignment(QtCore.Qt.AlignLeft)

        self.queue = QLabel("Ingen kø", self)
        self.queue.setStyleSheet("color: black; background-color: white; margin:2px; border:2px solid rgb(125, 125, 125); font-size: 20pt; font-family:  ;")
        #self.queue.resize(200, 100)
        self.queue.setAlignment(QtCore.Qt.AlignCenter)
    
        
        


        ###Design###
        hbox = QHBoxLayout()
        #hbox.addStretch(0)
 
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.arrivedButton)
        vbox1.addStretch(2)
        vbox1.addWidget(self.cur_room_label)
        vbox1.addWidget(self.cur_room)
        vbox1.addStretch(1)
        vbox1.addWidget(self.next_room_label)
        vbox1.addWidget(self.next_room)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.nextButton)
        vbox2.addStretch(1)
        vbox2.addWidget(self.queue_label)
        vbox2.addWidget(self.queue)


        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
 
        self.setLayout(hbox)
 
        self.setGeometry(0, 20, 400, 400)
        self.setWindowTitle('HealthCAT Mockup')
        self.show()


__all__ = ['mqtt_server_node']

