#!/usr/bin/python
"""
--------------------
HAWK-I PIPELINE v0.0
--------------------

SCHEDULER:

	Determines if a GRB is observable at paranal in the next 4 hours

Usage:
	python hawki_schedule.py -ra RA -dec DEC -equinox EQUINOX -time TIME
"""

import time
import sys

from remoteObserver.lib.cooReWrapperClass import CelestialObject

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2011"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"

def main():
	# Script outline
	# 
	# 1. When is the object visible from Paranal?
	# 2. Is it visible within 4 hours after the trigger?
	# 3. Is it visible long enough (~ 1hr)
	
	RA = "23:18:11.57"
	DEC = "32:28:31.8"
	EQUINOX = "J2000"
	# Format for my script = ?!? skycat!!!
	#TRIGGER = 

	# Example usage
	# Set the observatory information and calc twilights
	GRB = CelestialObject()
	GRB.setObservatory(siteabbrev='e')
	intime = [2012, 06, 23, 10, 10, 10, 0, 0, 0]
	timestruct = time.struct_time(intime[0:9])
	GRB.computeTwilights(intime=timestruct)
	GRB.computeNightLength()
	GRB.printInfo()

if __name__ == "__main__":
	main()
# Mon Dec 19 16:58:00 CET 2011
