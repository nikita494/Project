# -*- coding: utf-8 -*-

import pytesseract
import subprocess, re
import time
import RPi.GPIO as GPIO
from PIL import Image
from threading import Thread

volume = 50
play = True
flag_start = True
mas = ["Здравстуйте!", "Устройство включено."]

KEY_start = 7
KEY_pause = 8
KEY_up_volume = 9
KEY_down_volume = 10

def processing():
    global play
    global flag_start
    global mas
    
    for z in mas[:]:
        if not play:
            print("Killing")
            subprocess.Popen('pkill -9 RHVoice-text', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            break
        s = 'echo "' + z + '" | RHVoice-test -p anna'
        subprocess.call(s, shell=True)
        mas.remove(z)
    else:
        print("Breaking")
    

def up_volume():
    global volume
    if volume < 100: 
        volume += 10
    subprocess.call("amixer sset Master {}%".format(volume), shell=True)
    
def down_volume():
    global volume
    if volume > 0: 
        volume -= 10
    subprocess.call("amixer sset Master {}%".format(volume), shell=True)

def start():
    global text
    global mas
    img = Image.open('/home/pi/Desktop/scan.jpg')
    text = pytesseract.image_to_string(img, config='-l rus --oem 3 --psm 1').replace('-', '').replace('\n', '').replace('\t', '').replace('\r', '').replace('..', '.').replace('.', '. ')
    print(text)
    mas = re.split("\\b[.!?\\n]+(?=\\s)", text)
    processing()
    
def pause():
    global play
    global flag_start
    if not flag_start:
        play = not play
        print("Play is", play)
        if play:
            processing()
        
    
subprocess.call("amixer sset Master {}%".format(volume), shell=True)
processing()
mas = []

GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY_start, GPIO.IN)
GPIO.setup(KEY_pause, GPIO.IN)
GPIO.setup(KEY_up_volume, GPIO.IN)
GPIO.setup(KEY_down_volume, GPIO.IN)

while True:
    if mas == []:
        flag_start = True
    else:
        flag_start = False
    if GPIO.input(KEY_start) == False and flag_start:
        print("Start")
        th = Thread(target=start)
        th.start()
        mas = ["."]
        time.sleep(0.3)
    if GPIO.input(KEY_pause) == False:
        th = Thread(target=pause)
        th.start()
        time.sleep(0.3)
    if GPIO.input(KEY_up_volume) == False:
        th = Thread(target=up_volume)
        th.start()
        time.sleep(0.3)
    if GPIO.input(KEY_down_volume) == False:
        th = Thread(target=down_volume)
        th.start()
        time.sleep(0.3)
