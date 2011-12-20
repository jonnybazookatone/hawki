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

import sys
import numpy
import datetime
import time

from pyservatory.cooReWrapperClass import CelestialObject
import pyservatory.cooclasses as coo

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2011"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"


def main(RA, DEC, EQUINOX, TRIGGERTIME):
	# Script outline
	# 
	# 1. When is the object visible from Paranal?
	# 2. Is it visible within 4 hours after the trigger?
	# 3. Is it visible long enough (~ 1hr)

	# Set the observatory information and calc twilights
	GRB = CelestialObject()
	GRB.setObservatory(siteabbrev='e')
	GRB.computeTwilights()
	GRB.computeNightLength()
	JulianDayNOW = GRB._OBJECTWRAPPER.jd
	GRB.setRADEC(RA=RA, DEC=DEC, EQUINOX=EQUINOX)
	GRB.setTRIGGER(TRIGGERTIME)
	GRB.printInfo()
	sys.exit(0)
	#GRB.plotNightAltitude()
	#GRB._Figures = GRB._Figures - 1
	#GRB.plotNightVisibility()
	
	
	# Check if the GRB is observable
	triggerDelay = 4 # hours
	exposureTime = 1 # hours
	
	JulianDayNOW = GRB._OBJECTWRAPPER.jdsunset + 1/48. # temp
	starttime = GRB._OBJECTWRAPPER.jdsunset # temp
	triggertime = GRB._OBJECTWRAPPER.jdsunset+3/24. # temp
	fullVisibilityArray = GRB.computeNightVisibility(telescopelimit=20, triggerdelay=(4/24.), triggertime=triggertime)
	

	
	if len(fullVisibilityArray) == 0:
		print "### ATTENTION ###"
		print "Plan: do NOT trigger VLT"
		print ""
		print "REASONS"
		print "No observability period."
		print ""
		print "DETAILS"
		print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
		print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
		print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
		triggerFlag = False
	
	else:
		# Trigger outline
		#
		# 1. pick times that are greater than the trigger time
		# 2. is the length of the observation greater than 1 hour? - if we trigger before the obs period
		# 3. is the end of the observation - NOW, greater than 1 hour?  -  if we trigger during the obs period
		# 4. is the observable time < 4 hours after the triggerDelay
	  
		for i in range(len(fullVisibilityArray)):
			# Trigger flag
			triggerFlag = True

			# 1. pick times that are greater than the trigger time
			TimeArray = fullVisibilityArray[i][1] # for 1.
			tmpTimeArray = numpy.array([])
			for i in range(len(TimeArray)):
				if TimeArray[i] >= triggertime:
					tmpTimeArray = numpy.append(tmpTimeArray, TimeArray[i])
					
			print "Possible observability"
			print GRB.jd2skycalcstruct(tmpTimeArray[0])
			print GRB.jd2skycalcstruct(tmpTimeArray[-1])
			print ""

			# all the times needed
			# ATTENTION - TIMES WILL BE IN HOURS FOR COMPARISON
			LengthOfObservability = (tmpTimeArray[-1]-tmpTimeArray[0]) * 24 # for 2.
			LengthOfObservabilityFromNow = (tmpTimeArray[-1] - JulianDayNOW) * 24 # for 3.
			TimeBetweenTriggerAndHAWKI = (tmpTimeArray[0] - triggertime) * 24. # for 4.

			if len(tmpTimeArray) == 0:
				print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "No observability period."
				print ""
				print "DETAILS"
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
				triggerFlag = False
		  
			# 2. is the length of the observation greater than 1 hour? - if we trigger before the obs period
			if LengthOfObservability < exposureTime:
				print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
				triggerFlag = False

			# 3. is the end of the observation - NOW, greater than 1 hour?  -  if we trigger during the obs period
			if LengthOfObservabilityFromNow < exposureTime:
				print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "If we trigger now, we do not have enough time to expose."
				print "dt = now - end of observability = %s" % (LengthOfObservabilityFromNow)
				print ""
				print "DETAILS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
				triggerFlag = False

			# 4. is the observable time < 4 hours after the triggerDelay
			TimeBetweenTriggerAndHAWKI = (tmpTimeArray[0] - triggertime) * 24.
			if TimeBetweenTriggerAndHAWKI > triggerDelay:
				print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "The VLT trigger time is > 4 hours after the GRB trigger time."
				print "dt = %s" % (TimeBetweenTriggerAndHAWKI)
				print ""
				print "DETAILS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
				triggerFlag = False

			
	return triggerFlag
	

if __name__ == "__main__":
  
	# Test cases
  
	RA = "06:30:45.50"
	DEC = "-60:31:12.0"
	EQUINOX = "J2000"
	TRIGGERTIME = time.struct_time((2011, 12, 10, 9, 43, 0, 0, 0, 0))
	TRIGGERTIME = coo.time_to_jd(TRIGGERTIME[0:6])

	#RA = "23:18:11.57"
	#DEC = "32:28:31.8"
	main(RA, DEC, EQUINOX, TRIGGERTIME)
	#if main():
		#print "TRIGGER!!!!"
	#else:
		#print "NOOOOO!!!!!"
# Mon Dec 19 16:58:00 CET 2011
