import os
import glob
import time

import numpy as np
import matplotlib.pyplot as plt

import datetime as dt
import csv



# system commands for initilizing the temp sensor and onw-wire comm.
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# see menual how to find the devices location
deviceAddress = '28-011430163dad'
device_file = '/sys/bus/w1/devices/' +deviceAddress +'/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(isDebug):
    if isDebug:
        temp_c =int(dt.datetime.now().strftime('%S')) #np.random.randint(20,30,1)[0] # select the first (and only) array componenet
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
    
def saveSamplesToLog(CurrTime,unsavedTimeSamples,unsavedTempSamples):
    # Check if the path exists
    tempLogPath = 'logs/tempSensor/'+ CurrTime.strftime('%Y_%m')+ '/'+CurrTime.strftime('%d')+'/'+'log_tempSens_'+CurrTime.strftime('%Y_%m_%d')+'.csv'
    isCurrTempLogExists = os.path.exists(tempLogPath)
    
    if isCurrTempLogExists: # if the file exists append new data.
        # Open existing CSV file in append mode
        # Create a file object for this file
        with open(tempLogPath,'a',newline='') as fObj:
            # Pass this file object to csv.writer()
            # and get a writer object
            writerObj = csv.writer(fObj)
            
            # Loop over data and write each row
            for iData in range(len(unsavedTempSamples)):
                list2write = [unsavedTimeSamples[iData],unsavedTempSamples[iData]]
                writerObj.writerow(list2write)
            
            # Close the file object
            fObj.close()
    else:
        # the file dosnt exists, gen the path
        tempLogPath = 'logs/tempSensor/'+ CurrTime.strftime('%Y_%m')+ '/'+CurrTime.strftime('%d')+'/'
        os.makedirs(tempLogPath)
        fPath = tempLogPath + 'log_tempSens_'+CurrTime.strftime('%Y_%m_%d')+'.csv'
        
        # write the data
        with open(fPath,'w',newline='') as fileObj:
            writerObj=csv.writer(fileObj)
            for iData in range(len(unsavedTempSamples)):
                list2write = [unsavedTimeSamples[iData],unsavedTempSamples[iData]]
                writerObj.writerow(list2write)
            fileObj.close()
    print(str(CurrTime)+' Log Saved to: ' + tempLogPath)
    return


def loadSamplesFromLog(CurrTime):
    timeSamples = []
    tempSamples = []
    tempLogPath = 'logs/tempSensor/'+ CurrTime.strftime('%Y_%m')+ '/'+CurrTime.strftime('%d')+'/'+'log_tempSens_'+CurrTime.strftime('%Y_%m_%d')+'.csv'
    isCurrTempLogExists = os.path.exists(tempLogPath)
    
    if isCurrTempLogExists:
        with open(tempLogPath ,'r') as fileObj:
            reader = csv.reader(fileObj)
            for row in reader:
                timeSamples.append(row[0])
                tempSamples.append(float(row[1]))
            fileObj.close()
            print(str(CurrTime)+' Log Loded from: ' + tempLogPath)
    return [timeSamples,tempSamples]




# Code starts here
isDebug = False

# Plot Config
maxSmaples = 24*60*60
numPlotTimeStamps = 24
xTicksFontSize = 8
figTempSizeX=10
fifTempSizeY=6
logSaveInterval = 60 #Seconds

# Var init
unsavedTempSamples = []
unsavedTimeSamples = []
savedTempSamples = []
savedTimeSamples = []
loopRunTimeStr = '0'
plotRunTimeStr = '0'

# Data files config
CurrTime        = dt.datetime.now()
lastSaveTime    = dt.datetime.now()

[savedTimeSamples, savedTempSamples] = loadSamplesFromLog(CurrTime)
[pastTimeSamples, pastTempSamples] = loadSamplesFromLog(CurrTime-dt.timedelta(days=1)) # Date input "yestraday"     

deltaTimeSave = dt.timedelta(seconds = logSaveInterval)
while True:
    
    # Read new data
    CurrTime   = dt.datetime.now()
    currTemp   = read_temp(isDebug)
    curTimeStr = CurrTime.strftime('%H:%M:%S.%f')
    
    # If new day save the past samples
    if CurrTime.date() > lastSaveTime.date():
        # save the unsaved samples and append them to the saved list samples
        saveSamplesToLog(CurrTime,unsavedTimeSamples,unsavedTempSamples)
        lastSaveTime    = dt.datetime.now()
        savedTempSamples.append(unsavedTempSamples)
        savedTimeSamples.append(unsavedTimeSamples)
        
        # As it is a new day, dump the past samples (wich are now 2 days old) and the replace them with saved samples (which are now one day old)
        pastTempSamples = []
        pastTimeSamples = []
        pastTempSamples.append(savedTempSamples)
        pastTimeSamples.append(savedTimeSamples)
        
        # clear the saved samples as they are from the previus day.
        savedTempSamples = []
        savedTimeSamples = []
        
        # clear the unsaved samples as they were just saved.
        unsavedTempSamples = []
        unsavedTimeSamples = []
       
    # Append the new samples to the unsaved list
    unsavedTempSamples.append(currTemp)
    unsavedTimeSamples.append(curTimeStr)
    
    # Check if the new samples are needed to be saved
    if CurrTime - lastSaveTime > deltaTimeSave:
        saveSamplesToLog(CurrTime,unsavedTimeSamples,unsavedTempSamples)
        savedTempSamples = savedTempSamples + unsavedTempSamples
        savedTimeSamples = savedTimeSamples + unsavedTimeSamples
        unsavedTempSamples = []
        unsavedTimeSamples = []
        lastSaveTime    = dt.datetime.now()
    
    tempVec = pastTempSamples + savedTempSamples + unsavedTempSamples
    timeVec = pastTimeSamples + savedTimeSamples + unsavedTimeSamples

        
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
    
    plotStartTime = dt.datetime.now()
    #plt.figure(figsize=(figTempSizeX,fifTempSizeY))
    plt.clf() # Clears the plot
    plt.plot(timeVec,tempVec)
    plt.ylabel('Temp. [C]')
    plt.xticks(xTicks2show, labels2show, rotation=45, ha='right', fontsize=xTicksFontSize)
    plt.title(label = CurrTime.strftime('%H:%M:%S') +'  ' + str(currTemp) + ' [C]' + 'len=' + str(lenTimeVec) + ' loop:'+loopRunTimeStr+' plot:'+plotRunTimeStr)
    plt.grid()
    plt.show(block=False) # if block=True script will stop at this line until the figure close
    plt.pause(0.05)
    
    if isDebug:
        time.sleep(1)
    
    loopEndTime = dt.datetime.now()
    loopRunTimeObj = loopEndTime-CurrTime
    loopRunTimeStr = str(loopRunTimeObj)
    
    plotRunTimeObj = loopEndTime-plotStartTime
    plotRunTimeStr = str(plotRunTimeObj)