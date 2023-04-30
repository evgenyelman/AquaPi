import os
import glob
import time

import numpy as np
import matplotlib.pyplot as plt

import datetime as dt




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

# Plot Config
maxSmaples = 24*60*60
numPlotTimeStamps = 24
figTempSizeX=10
fifTempSizeY=6

# Var init
tempVec = []
timeVec = []
while True:
    
    currTemp = read_temp(isDebug)
    curTime  = dt.datetime.now().strftime('%H:%M:%S.%f');
    
    tempVec.append(currTemp)
    timeVec.append(curTime)

    
    lenTempVec = len(tempVec)
 
    # Dump old samples if over float
    if lenTempVec>maxSmaples:
        tempVec = tempVec[lenTempVec-maxSmaples:]
        timeVec = timeVec[lenTempVec-maxSmaples:]
   
    # Should be a checker that the above arrays are with the same length.
    
    lenTimeVec = len(timeVec)
    dsFac = np.ceil(lenTimeVec/numPlotTimeStamps) # The downsample factor, int is required for sliceing
    xTicks2show = range(0,lenTimeVec,int(dsFac))
    
    labels2show=[]
    for oldIdx in  xTicks2show:
        labels2show.append(timeVec[oldIdx][:-7])
    
    plt.figure(figsize=(figTempSizeX,fifTempSizeY))
    plt.clf() # Clears the plot
    plt.plot(timeVec,tempVec)
    plt.ylabel('Temp. [C]')
    plt.xticks(xTicks2show, labels2show, rotation=45, ha='right')
    plt.show(block=False) # if block=True script will stop at this line until the figure close
    plt.pause(0.05)