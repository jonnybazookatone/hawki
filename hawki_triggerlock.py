#!/usr/bin/python
"""Default python script layout."""

import sys
import os
import glob
import time
import re
import shutil
import logging

from hawki_burstinfo import main as burstinfo
from hawki_ftp_upload import makeRRMFile, uploadRRMFile
from hawki_email_send import email_send
from hawki_make_fc import hack_fc, upload_fc
from hawki_mounted import mounted 
from hawki_schedule import main as observability
import lib.pyservatory.cooclasses as coo

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2011"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"

def check4burst(RA, DEC, EQUINOX, TRIGGERTIME, NAME):

	# Logging
	logfmt = '%(levelname)s:  %(message)s\t(%(asctime)s)'
	datefmt= '%m/%d/%Y %I:%M:%S %p'
	formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
	logger = logging.getLogger('__main__')
	logging.root.setLevel(logging.DEBUG)

	if not os.path.isdir("logs"): os.mkdir("logs")
	fh = logging.FileHandler(filename='logs/%s_lock.log' % NAME) #file handler
	fh.setFormatter(formatter)
	#logger.addHandler(ch)
	logger.addHandler(fh)
	logger.info("\n\nTRIGGER LOCK DETAILS: CREATION\n\n")


	# 2. MOUNTED
	#
	# Check old file exists, rrmLog_WebStatus.html
		
	filename = "%s/%s" % (sys.path[0], "rrmLog_WebStatus.html")
	if glob.glob(filename):
		os.remove(filename)

	Mounted = mounted(NAME, verbose=True)

	# 3. OBSERVABLE
	#
	
	Observability, obstime = observability(RA, DEC, EQUINOX, TRIGGERTIME, NAME)


	# Possible outcomes
	# Mounted	|	Observable 	|	 Trigger
	#
	# Yes		|	Yes		|	Yes
	# Yes		|	No		|	No
	# No		|	Yes		|	No
	# No		|	No		|	No
	# Yes		|	Later		|	Later
	# No		|	Later		|	No

	# 4. Write LOCK file
	Mounted = True
	if Mounted & Observability:
		lockfilename = "lock/%s.rrm" % (NAME)

		if glob.glob(lockfilename):
                        logger.info("THIS TRIGGER HAS ALREADY BEEN CREATED, EXITING.")
		else:
			lockfile = open(lockfilename, "w")
	                lockfile.write("%s %s %s %s %s\n" % (RA, DEC, NAME, obstime[0],obstime[-1]))
	                lockfile.close()
		
	return Observability & Mounted

def check4trigger(force=False):

	# Logging
	logfmt = '%(levelname)s:  %(message)s\t(%(asctime)s)'
	datefmt= '%m/%d/%Y %I:%M:%S %p'
	formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
	logger = logging.getLogger('__main__')
	logging.root.setLevel(logging.DEBUG)

	if not os.path.isdir("logs"): os.mkdir("logs")
	fh = logging.FileHandler(filename='logs/%s_lock.log' % NAME) #file handler
	fh.setFormatter(formatter)
	#logger.addHandler(ch)
	logger.addHandler(fh)
	logger.info("TRIGGER LOCK DETAILS: SURVEILLANCE\n\n")

	# Checks if there is a trigger that should be called

	logger.info("Checking for RRM triggers awaiting HAWK-I triggering\n")
  
	# FROM DOC
	# --------
        # OPTIONS:
	#        1. New trigger GRBNAME.rrm
        #        2. New trigger, triggered GRBNAME.rrmlock

        # a. Trigger lock exists; yes/no
        # b. if Trigger exists; New; yes/no
        # c. if Trigger exists; if New;

        #        c.1. Upload FTP file
        #        c.2. E-mail details
        #        c.3. Finding Chart
        #        (c.4. text message)

	
	# Check the lock folder
	rrmLocks = glob.glob("lock/*")
	newTrigger = []
	previousTriggers = []
	
	if rrmLocks:
		for rrmburst in rrmLocks:
			pattern = 'rrmlock'
			if re.search(pattern, rrmburst):
				logger.info("RRM LOCKED IGNORING BURST: %s" % rrmburst)
				previousTriggers.append(rrmburst)

			else:
				logger.info("RRM TRIGGER: %s" % rrmburst)
				newTrigger.append(rrmburst)

		for burst in newTrigger:

			# Trigger RRM
			# Collect the details
			rrmfile = open(burst, "r")
			rrmdata = rrmfile.readlines()[0].split(" ")
			rrmfile.close()
			
			rrmRA = rrmdata[0]
			rrmDEC = rrmdata[1]
			rrmName = rrmdata[2]
			rrmStart = float(rrmdata[3])
			rrmEnd = float(rrmdata[4])
			
			logger.info("Details of opened trigger")
			logger.info("rrmRA: %s" % rrmRA)
			logger.info("rrmDEC: %s" % rrmDEC)
			logger.info("rrmName: %s" % rrmName)
			logger.info("rrmStart: %s JD" % rrmStart)
			logger.info("rrmEnd: %s JD" % rrmEnd)
			
			# First we have  to check if we can trigger
			if not force:
				JulianDayNOW = coo.time_to_jd(time.gmtime(time.time())[0:6])
				TimeBetweenNowAndTrigger = JulianDayNOW - rrmStart
				if TimeBetweenNowAndTrigger > 0:
					logger.info("!!! TRIGGERING !!!")
					# Move the file to a locked rrm trigger
					shutil.move(burst, "%slock" % burst)
					
				else:
					
					logger.info("This trigger is in the future")
					logger.info("Time until trigger: %.2f hours" % (abs(TimeBetweenNowAndTrigger*24)))
					break

			# 1. Upload FTP
			logger.info("\nBeginning RRM Upload")
			OBName = "RRM_GRB_AUTO_1"
			RRMFile = makeRRMFile(rrmRA, rrmDEC, rrmName, OBName)
			uploadRRMFile(RRMFile)
			logger.info("Finished RRM Upload")

			# 2. Finding Chart
			logger.info("\nBeginning FC Creation")
			FindingChartName = "fc/%s.jpg" % (rrmName)
			FindingChartURL = "http://jonnyy.uwcs.co.uk/grbs/%s.jpg" % (rrmName)
			rrmError = 600
			hack_fc(rrmRA, rrmDEC, rrmName, rrmError)
			upload_fc(FindingChartName)
			logger.info("Finished FC Creation")

			# 3. E-mail details
			logger.info("\nBeginning E-mail Sending")
			email_send(FindingChartURL, rrmName, OBName, rrmRA, rrmDEC)
			logger.info("Finished E-mail Sending")

	else:
		logger.info("NO TRIGGERS, EXITING")


if __name__ == "__main__":
	
	# Test cases

	# Mounted + Observable


        # Trigger something observable at night
        # Expected: TRIGGER
        # 1. GRB INFO FROM JCG PAGES
	grblist = burstinfo()
	
	for grb in grblist:
		#RA = "06:30:45.50"
		#DEC = "-60:31:12.0"
		#EQUINOX = "J2000"
		#NAME = "TEST"
		#TRIGGERTIME = time.struct_time((2012, 01, 10, 23, 43, 0, 0, 0, 0))
		
		RA = grb.getRA()
		DEC = grb.getDEC()
		EQUINOX = "J2000"
		NAME = grb.getName()
		TRIGGERTIME = grb.getTIME()
		TRIGGERTIME = coo.time_to_jd(TRIGGERTIME[0:6])
        
		if not check4burst(RA, DEC, EQUINOX, TRIGGERTIME, NAME):
			print "\nExpected result"
		else:
			print "WARNING: FAILED!!!"

        #print "\n\n\n\n\n"

	#check4trigger()

# Tue Dec 20 18:53:04 CET 2011
