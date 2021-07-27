from labjack import ljm
from time import sleep

def rating(rateLevel=200, DT=100, HT=500, HTT=1000):
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")

    # print labjack info
    print(ljm.getHandleInfo(handle), "deviceType, connectionType, serialNumber, ipAddress, portOrPipe, packetMaxBytes")
       
    # Setup and call eReadAddresses to read values from the LabJack.
    numFrames = 4
    aAddresses = [46000, 46002, 46004, 46006]  # [rateLevel, DT, HT, HTT, RR interval]
    aDataTypes = [ljm.constants.FLOAT32, ljm.constants.FLOAT32, ljm.constants.FLOAT32, ljm.constants.FLOAT32, ljm.constants.FLOAT32]            
    aValues =  [rateLevel, DT, HT, HTT]  # in uAmps       
    ljm.eWriteAddresses(handle, numFrames, aAddresses, aDataTypes, aValues,)            
    print(ljm.eReadAddresses(handle, numFrames, aAddresses, aDataTypes), "rateLevel, DT, HT, HTT in uAmps")
    print(ljm.eReadAddress(handle, 0, 3)*84/5.0992, "RR interval") 

    ljm.eWriteAddress(handle, 46010, 1, 1)  # Set pause flag
    print(ljm.eReadAddress(handle, 46010, 1), "pause flag") # read pause flag

    # ljm.eWriteName(handle, "LUA_RUN", 1)
 
    stimBack = rateLevel/10
    print(stimBack, "rateLevel/10")

    return stimBack

    # Close handle
    # ljm.close(handle)
