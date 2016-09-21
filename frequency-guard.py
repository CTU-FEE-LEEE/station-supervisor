#!/usr/bin/python
#
# Sample of measuring and frequency correction with ACOUNTER02A

import time
import datetime
import sys
from pymlab import config
import os
from mlabutils import ejson
import numpy as np


#import logging
#logging.basicConfig(level=logging.DEBUG)

parser = ejson.Parser()

if len(sys.argv) != 3:
    sys.stderr.write("Invalid number of arguments. Missing path to a config files!\n")
    sys.stderr.write("Usage: %s config_file.json i2c_bus.cfg\n" % (sys.argv[0], ))
    sys.exit(1)

value = parser.parse_file(sys.argv[1])

# path to metadata output directory
path = value['configurations'][0]['children'][0]['metadata_path']

# required frequency
carrier_freq = value['configurations'][0]['children'][0]['transmitter_carrier']	# Beacon frequency
low_detect_freq = value['configurations'][0]['children'][0]['children'][1]['low_detect_freq']
hi_detect_freq = value['configurations'][0]['children'][0]['children'][1]['hi_detect_freq']

echo_freq = (hi_detect_freq + low_detect_freq)/2	# hearing frequency
req_freq = (carrier_freq - echo_freq) * 2

# station name
StationName = value['configurations'][0]['children'][0]['origin']

print "RMDS Station Local Oscillator Tunning Utility \r\n"

#### Sensor Configuration ###########################################

while True:


	cfg = config.Config()
	cfg.load_file(sys.argv[2])

	try:
		cfg.initialize()

		fcount = cfg.get_device("counter")
		fgen = cfg.get_device("clkgen")
		time.sleep(0.5)
		fcount.route()
		current_freq = fcount.get_freq()
		fcount.route()
		fcount.set_GPS()	# set GPS configuration
		frequencies = np.array([current_freq])


		#### Data measurement and logging ###################################################


		sys.stdout.write("\r\nCarrier Freq.: %3.6f MHz, Echo Freq.: %3.3f kHz, Req. Freq.: %3.6f MHz\r\n\n" % (carrier_freq/1e6, echo_freq/1e3, req_freq/1e6))

		while True:
		    now = datetime.datetime.now()
		    filename = path + time.strftime("%Y%m%d%H", time.gmtime())+"0000_"+StationName+"_freq.csv"
		    if not os.path.exists(filename):
		        with open(filename, "a") as f:
		            f.write('#timestamp,LO_Frequency \n')

		    if (now.second == 15) or (now.second == 35) or (now.second == 55):
		        fcount.route()
		        current_freq = fcount.get_freq()
		        with open(filename, "a") as f:
		            f.write("%.1f,%.1f\n" % (time.time(), current_freq))

		        freq_error = current_freq - req_freq

			if (freq_error > frequencies.std()):                # set new parameters to oscilator only if the error is large or if we have enought statistics to madify the frequency
			    fgen.route()
			    regs = fgen.set_freq(frequencies.mean()/1e6, float(req_freq/1e6))
			else:
			    frequencies = np.append(frequencies, current_freq)
			    if (len(frequencies) > 10):
				frequencies = np.delete(frequencies, 0)
				#print frequencies
		
		    sys.stdout.write("Current Freq.: %3.7f MHz, Req. Freq.: %3.6f MHz, Freq Error: %3.1f Hz, Time: %d s \r" % (current_freq/1e6, req_freq/1e6, (current_freq - req_freq), now.second ))
		    sys.stdout.flush()
		    time.sleep(0.9)

	except IOError:
		sys.stdout.write("\r\n************ I2C Error\r\n")
		time.sleep(5)

	except KeyboardInterrupt:
		sys.stdout.write("\r\n")
		sys.exit(0)
	

