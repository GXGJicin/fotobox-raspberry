from socket import *

import thread

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
'''
while True:
    input_state = GPIO.input(18)
    if input_state == False:
        print('Button Pressed')
        time.sleep(0.2)
'''

stav = False

host = '0.0.0.0'
port = 4321
buf = 1024

addr = (host, port)

serversocket = socket(AF_INET, SOCK_STREAM)
serversocket.bind(addr)
serversocket.listen(2)

clients = [serversocket]

def handler(clientsocket, clientaddr):
    global stav
    print "Accepted connection from: ", clientaddr
    while True:
        data = clientsocket.recv(1024)
        if "exit" in data or not data:
            break
        elif "stav" in data:
            if stav:
                clientsocket.send("ZAPNUTO\n")
            else:
                clientsocket.send("VYPNUTO\n")
        else:
            print data
            msg = "ECHO: %s" % data
            clientsocket.send(msg)

    clients.remove(clientsocket)
    clientsocket.close()

def tlacitko():
    global stav
    while True:
        if GPIO.input(18) == False:
            print 'Button Pressed'
            stav = True
            '''
            for i in clients:
                if i is not serversocket:
                    i.send("ZAPNUTO\n")
            '''
        else:
            stav = False
            '''
            for i in clients:
                if i is not serversocket:
                    i.send("VYPNUTO\n")
            '''

        time.sleep(0.5)


thread.start_new_thread(tlacitko, ())

while True:
    print "Server is listening for connections\n"

    clientsocket, clientaddr = serversocket.accept()
    clients.append(clientsocket)
    thread.start_new_thread(handler, (clientsocket, clientaddr))

serversocket.close()