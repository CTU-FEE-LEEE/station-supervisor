#!/usr/bin/python

#%load_ext autoreload
#%autoreload 2

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

#### Sensor Configuration ###########################################

cfg = config.Config(
	i2c = {"port": 0},
        bus = [
            {
                "type": "i2chub",
                "address": 0x73,
                "children": [
                    {"name": "i2cspi", "type": "i2cspi" , "channel": 0, "address": 44 },
                    {"name": "lighting", "type": "LIGHTNING01A", "TUN_CAP": 6, "channel": 5, },
                ],
            },
        ],
)

sensor = cfg.get_device("lighting")

time.sleep(0.5)
#sensor.reset()

#print("Start Antenna tunnig.")
#sensor.antennatune_on(FDIV=0,TUN_CAP=6)
#time.sleep(50)
#sensor.reset()

#time.sleep(0.5)

sensor.calib_rco()

sensor.setWDTH(1)
sensor.setNoiseFloor(4)
sensor.setIndoor(True)
sensor.setSpikeRejection(1)
sensor.setMaskDist(True)

time.sleep(0.5)


i=0

#### Data Logging ###################################################

try:
    while True:
        interrupts = sensor.getInterrupts()
        if any(value == True for value in interrupts.values()):

            print("sINTer:", interrupts, datetime.datetime.now().isoformat(' '))
            print("WDTH:",sensor.getWDTH())
            print("TUN_CAP:",sensor.getTUN_CAP())
    #        print("power: ", sensor.getPowerStatus())
            print("indoor:", sensor.getIndoor())
            print("Noise floor is {} uVrms".format(sensor.getNoiseFloor()))
            print("Spike rejection 0b{:04b}".format(sensor.getSpikeRejection()))
            print("single Energy:", sensor.getSingleEnergy())
            print("Mask disturbance:", sensor.getMaskDist())
            print("Storm is {:02d} km away".format(sensor.getDistance()))

            time.sleep(0.5)

            i += 1

        else:
            time.sleep(5)

except KeyboardInterrupt:
    sys.exit(0)
