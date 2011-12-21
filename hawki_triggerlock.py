#!/usr/bin/python
"""Default python script layout."""

import sys
import os
import glob
import time
import re

from hawki_mounted import mounted 
from hawki_schedule import main as observability
import pyservatory.cooclasses as coo

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2011"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"

def check4burst(RA, DEC, EQUINOX, TRIGGERTIME, NAME):

	# 1. GRB INFO FROM JCG PAGES

	# 2. MOUNTED
	#
	# Check old file exists, rrmLog_WebStatus.html
		
	filename = "%s/%s" % (sys.path[0], "rrmLog_WebStatus.html")
	if glob.glob(filename):
		os.remove(filename)

	Mounted = mounted(verbose=True)

	# 3. OBSERVABLE
	#
	
	Observability, obstime = observability(RA, DEC, EQUINOX, TRIGGERTIME)


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
                        print "THIS TRIGGER HAS ALREADY BEEN CREATED, EXITING."
		else:
			lockfile = open(lockfilename, "w")
	                lockfile.write("%s %s %s %s %s\n" % (RA, DEC, NAME, obstime[0],obstime[-1]))
	                lockfile.close()
		
	return Observability & Mounted

def check4trigger():

	# Checks if there is a trigger that should be called

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
	if rrmLocks:
		for rrmburst in rrmLocks:
			pattern = 'rrmlock'
			if re.search(pattern, rrmburst):
				print rrmburst

	
	else:
		print "NO TRIGGERS, EXITING"


if __name__ == "__main__":
	
	# Test cases

	# Mounted + Observable


        # Trigger something observable at night
        # Expected: TRIGGER
        RA = "06:30:45.50"
        DEC = "-60:31:12.0"
        EQUINOX = "J2000"
	NAME = "TEST"
        TRIGGERTIME = time.struct_time((2011, 12, 21, 23, 43, 0, 0, 0, 0))
        TRIGGERTIME = coo.time_to_jd(TRIGGERTIME[0:6])
        if check4burst(RA, DEC, EQUINOX, TRIGGERTIME, NAME):
                print "\nExpected result"
        else:
                print "WARNING: FAILED!!!"

        print "\n\n\n\n\n"

	check4trigger()

# Tue Dec 20 18:53:04 CET 2011
