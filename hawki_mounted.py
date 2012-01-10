#!/usr/bin/python
"""###########################
HAWKI PIPELINE: MOUNT CHECK
###########################
To check if HAWKI is currently mounted on UT4 at the VLT.
"""

import re
import logging
import os

from lib.pyweb.webclass import CopiedWebPage

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2011"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"

# Script layout
#
# 1. Download the page with mounting information using wget
# 2. Parse the webpage
# 3. Return the user a True/False and information about the mounting

def mounted(NAME="TEST",verbose=True):
	# Logging
	logfmt = '%(levelname)s:  %(message)s\t(%(asctime)s)'
	datefmt= '%m/%d/%Y %I:%M:%S %p'
	formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
	logger = logging.getLogger('__main__')
	logging.root.setLevel(logging.DEBUG)

	if not os.path.isdir("logs"): os.mkdir("logs")
	fh = logging.FileHandler(filename='logs/%s_mnt.log' % NAME) #file handler
	fh.setFormatter(formatter)
	#logger.addHandler(ch)
	logger.addHandler(fh)
	logger.info("VLT INSTRUMENT DETAILS\n\n")


	HAWKIPage = CopiedWebPage()
	HAWKIPage.setFileName("rrmLog_WebStatus.html")
	HAWKIPage.getWebPage("http://www.eso.org/sci/facilities/paranal/sciops/RRM/rrmLog_WebStatus.html")
	HAWKIPage.parseWebPage()
	patternMount = "HAWKI"
	patternUT = "UT4/YEPUN"
	patternOnOff = "Online/"

	OnOff = False
	Mounted = False

	Content = HAWKIPage.getContent()

	if verbose:
		logger.info("rrmStatus Information")

	for i in range(len(Content)):

		line1 = Content[i]
		if i < len(Content)-1:
			line2 = Content[i+1]
		else:
			line2 = "None"

		# Is UT4 online
		if re.search(patternUT, line1) and re.search(patternOnOff, line2):
			if verbose:
				logger.info("%s STATUS: %s" % (line1.replace(" ", "").replace("<tdalign=center>", "").replace("</td>","").replace("\n",""), line2.replace(" ", "")))
				#print "%s" % (line1.replace(" ", ""))
				#print "%s\n" % (line2.replace(" ",""))
			OnOff = True


		# Is HAWKI online
		if re.search(patternMount, line1):
			if verbose:
				logger.info("HAWKI is mounted at the VLT.")
				logger.info("STATUS UT4: %s" % (line1.replace(" ","")))
			Mounted = True

	logger.info("End of rrmStatus information\n")

	# If UT4 is Online and HAWKI Mounted
	if OnOff and Mounted:
		if verbose:
			logger.info("UT4 is ONLINE and HAWKI is MOUNTED")
		returnFlag = True

	# If UT4 is Online but HAWKI not Mounted
	elif OnOff and not Mounted:
		if verbose:
			logger.info("UT4 is ONLINE but HAWKI is !NOT! MOUNTED")
		returnFlag = False

	# If UT4 is Offline but HAWKI not Mounted
	elif not OnOff and Mounted:
		if verbose:
			logger.info("UT4 is OFFLINE but HAWKI is MOUNTED")
		returnFlag = False

	# If UT4 is Offline and HAWKI is not Mounted
	elif not OnOff and not Mounted:
		if verbose:
			logger.info("UT4 is OFFLINE and HAWKI is !NOT! MOUNTED")
		returnFlag = False

	return returnFlag
	
def main():
	if mounted():
		print "PLAN: Trigger VLT"
	else:
		print "PLAN: Do not trigger VLT"
	
if __name__ == "__main__":
	main()
# Sat Dec 3 10:47:34 CET 2011
