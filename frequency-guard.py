#!/usr/bin/python
# 
# Sample of measuring and frequency correction with ACOUNTER02A

import time
import datetime
import sys
from pymlab import config
import os
import frequency_config

#### Sensor Configuration ###########################################

cfg = config.Config()
cfg.load_file("./bus_config.py")

cfg.initialize()

print "RMDS Station Local oscillator tunning utility \r\n"
fcount = cfg.get_device("counter")
fgen = cfg.get_device("clkgen")
time.sleep(0.5)
fcount.route()
frequency = fcount.get_freq()
fgen.route()
rfreq = fgen.get_rfreq()
hsdiv = fgen.get_hs_div()
n1 = fgen.get_n1_div()

fcount.route()
fcount.set_GPS()	# set GPS configuration


#### Data Logging ###################################################

try:
        while True:
            now = datetime.datetime.now()
            filename = frequency_config.path + time.strftime("%Y%m%d%H")+"0000_freq.csv"
            if not os.path.exists(filename):
                with open(filename, "a") as f:
                    f.write('#timestamp,LO_Frequency \n')

            if (now.second == 15) or (now.second == 35) or (now.second == 55):
                fcount.route()
                frequency = fcount.get_freq()
                with open(filename, "a") as f:
                    f.write("%.1f,%.1f\n" % (time.time(), frequency))


                #if (len(sys.argv) == 3):
                fgen.route()
                regs = fgen.set_freq(frequency/1e6, float(frequency_config.req_freq))
                now = datetime.datetime.now()

            fgen.route()
            rfreq = fgen.get_rfreq()
            hsdiv = fgen.get_hs_div()
            n1 = fgen.get_n1_div()
            fdco = (frequency/1e6) * hsdiv * n1
            fxtal = fdco / rfreq

            sys.stdout.write("Current Freq.: " + str(frequency/1e6) + " MHz ")
            sys.stdout.write("Req. Freq.: " + str(frequency_config.req_freq) + "MHz  Freq diff.: " + str(frequency - frequency_config.req_freq*1e6) + "Hz Time: " + str(now.second) + "s \r")

            sys.stdout.flush()

            time.sleep(0.9)

except KeyboardInterrupt:
    sys.stdout.write("\r\n")
    sys.exit(0)
    f.close()
