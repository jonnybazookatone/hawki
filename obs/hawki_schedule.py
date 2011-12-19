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

from pyservatory.cooReWrapperClass import CelestialObject

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

	# Set the observatory information and calc twilights
	GRB = CelestialObject()
	GRB.setObservatory(siteabbrev='e')
	GRB.computeTwilights()
	GRB.computeNightLength()
	JulianDayNOW = GRB._OBJECTWRAPPER.jd

	GRB.setRADEC(RA=RA, DEC=DEC, EQUINOX=EQUINOX)
	#GRB.setTRIGGER(TRIGGER)
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
		return False
	else:
	  
		for i in range(len(fullVisibilityArray)):
		  
			TimeArray = fullVisibilityArray[i][1]
			tmpTimeArray = numpy.array([])
			for i in range(len(TimeArray)):
				if TimeArray[i] >= JulianDayNOW:
					tmpTimeArray = numpy.append(tmpTimeArray, TimeArray[i])
		  
			if len(tmpTimeArray) == 0:
				print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
				return False
		  
			LengthOfObservability = (tmpTimeArray[-1]-tmpTimeArray[0]) * 24
			
			#if triggertime > JulianDayNOW:
			  
			#elif triggertime < JulianDayNOW:
			TimeBetweenTriggerAndHAWKI = tmpTimeArray[0] - triggertime
			
			if LengthOfObservability >= exposureTime and TimeBetweenTriggerAndHAWKI <= triggerDelay and TimeBetweenTriggerAndHAWKI > triggerDelay:
				print "### ATTENTION ###"
				print "Plan: DO trigger VLT"
				print ""
				print "REASONS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
			
			elif LengthOfObservability < exposureTime:
			  	print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print "Not observable for %s hour" % (exposureTime)
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
			
			elif TimeBetweenTriggerAndHAWKI > triggerDelay:
			  	print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print "Trigger is longer than: %s hours" % (triggerDelay)
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
			else:
			  	print "### ATTENTION ###"
				print "Plan: do NOT trigger VLT"
				print ""
				print "REASONS"
				print "Observable: %s hours" % (LengthOfObservability)
				print "Time until triggering: %s hours" % (TimeBetweenTriggerAndHAWKI)
				print "unexpected error"
				print ""
				print "Time of trigger:", GRB.jd2skycalcstruct(triggertime)
				print "Current time:", GRB.jd2skycalcstruct(JulianDayNOW)
				print "End of observability:", GRB.jd2skycalcstruct(TimeArray[-1])
			#print deltatimde
			
	sys.exit(0)
	
	
	print "Trigger: %s" % triggertime
	print "Start: %s" % starttime
	print "dT: %s hours" % ((triggertime-starttime)*24)
	
	if len(fullVisibilityArray) == 0:
		print "####################"
		print "INFO: NOT OBSERVABLE"
		print "####################"
	else:
		print "OBSERVABLE"
	#plt.show()
	#GRB.printInfo()

if __name__ == "__main__":
	main()
# Mon Dec 19 16:58:00 CET 2011
