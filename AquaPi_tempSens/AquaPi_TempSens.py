import os
import glob
import time

import numpy as np
import matplotlib.pyplot as plt



os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# see menual how to find the devices location
device_file = '/sys/bus/w1/devices/28-011430163dad/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(isDebug):
    if isDebug:
        temp_c = np.random.randint(20,30,1)
        return temp_c        
    else:
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c        
    


# Code starts here
isDebug = True
tempVec = np.empty(10)
while True:
    tempVec = np.roll(tempVec,-1)
    tempVec[-1] = read_temp(isDebug)

    plt.clf() # Clears the previus plot
    plt.plot(tempVec)
    plt.ylabel('some numbers')
    plt.show(block=False) # if block=True script will stop at this line until the figure closed
    plt.pause(0.05)

    print(tempVec)
    time.sleep(1)

