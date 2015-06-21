from socket import *

import thread

from subprocess import call
import subprocess, threading

# tutorial s tlacitkem http://razzpisampler.oreilly.com/ch07.html
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
port = 4322
buf = 1024

addr = (host, port)

serversocket = socket(AF_INET, SOCK_STREAM)
serversocket.bind(addr)
serversocket.listen(2)

clients = [serversocket]


def runCmdWithTimeout(cmd, timeout):
    process = None
    vratit = 0

    def target():
        print 'Thread started'
        process = subprocess.Popen(cmd, shell=True)
        process.communicate()
        print 'Thread finished'
        return vratit

    thread = threading.Thread(target=target)
    thread.start()

    thread.join(timeout)
    if thread.isAlive():
        print 'Terminating process'
        vratit = 1
        process.terminate()
        thread.join()
        return vratit
    return vratit
    #print process.returncode


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

        elif "nahled" in data:
            '''
            prikaz = "gphoto2 --set-config autofocusdrive=1 --capture-image-and-download --force-overwrite --filename FOTKA.JPG"
            print prikaz
            if runCmdWithTimeout(cmd=prikaz, timeout=20) == 0:
                print "nahled ok"
                prikaz2 = "convert FOTKA.JPG -quality 70 -resize 640x480 NAHLED.JPG"
                print prikaz2
                if runCmdWithTimeout(cmd=prikaz2, timeout=15) == 0:
                    print "nahled rozliseni ok"

                    soubor = "NAHLED.JPG"
                    bytes = open(soubor).read()
                    print len(bytes)
                    clientsocket.send(bytes)

                else:
                    print "vyfoceno rozliseni chyba"
            else:
                # FIXME: cely program spadne!
                print "nahled chyba"
            '''
            soubor = "NAHLED.JPG"
            bytes = open(soubor).read()
            print len(bytes)
            clientsocket.send(bytes)

        elif "fotka_ok" in data:
            # poslat fotku na server
            pass

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
            for i in clients:
                if i is not serversocket:
                    i.send("ZAPNUTO\n")
        else:
            stav = False
            for i in clients:
                if i is not serversocket:
                    i.send("VYPNUTO\n")


        time.sleep(0.5)


thread.start_new_thread(tlacitko, ())

while True:
    print "Server is listening for connections\n"

    clientsocket, clientaddr = serversocket.accept()
    clients.append(clientsocket)
    thread.start_new_thread(handler, (clientsocket, clientaddr))

serversocket.close()
