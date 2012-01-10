#!/usr/bin/python
"""Parses jochens webpage for bursts of the day."""

import datetime
import sys
import re
import time

from lib.pyweb.webclass import CopiedWebPage
from lib.pygrb.grbclass import GRB

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
# 1. Format the grb name for todays date in UTC
# 2. Download Jochens page for any combination of the following names
# 3. Find different details of the GRB that we want

def main(DefaultPage="http://www.mpe.mpg.de/~jcg"):

	# 1. 
	UTCNow = datetime.datetime.utcnow()
	if UTCNow.month < 10:
		month = "0%s" % UTCNow.month
	else:
		month = "%s" % UTCNow.month
	UTCName = "%s%s%s" % (UTCNow.year-2000,month, "06")
	#UTCName = "%s%s%s" % (UTCNow.year-2000,UTCNow.month, UTCNow.day)
	GRBPreFix = ['grb']
	GRBEndFix = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
	

	# 2.
	bursts = []
	for PreFix in GRBPreFix:
		for EndFix in GRBEndFix:
			
			GRBName = "%s%s%s" % (PreFix, UTCName, EndFix)
			Page = "%s/%s.html" % (DefaultPage, GRBName)

			newJochenPage = CopiedWebPage()
                        newJochenPage.setFileName(filename="bursts/%s.html" % GRBName)
			pageFlag = newJochenPage.getWebPage(url=Page)

			if pageFlag:
				print "%s: exists" % (GRBName)
				bursts.append(newJochenPage)
			else:
				print "%s: does not exist, stopping loop" % (GRBName)


	# 3.
	grblist = []
	for burst in bursts:

		# Look for:
		#
		# A. Co-ordinates: GRB_RA, GRB_DEC
		patternra, patterndec = "GRB_RA", "GRB_DEC"
		# B. Time of trigger: GRB_TIME
		patterntime = "GRB_TIME"
		# C. Sun distance: SUN_DIST
		patternsundist = "SUN_DIST"
		# D. Moon distance: MOON_DIST
		patternmoondist = "MOON_DIST"
		# E. Trigger time
		patterntriggertime = "NOTICE_DATE"
		

		burst.parseWebPage()
		burstcontent = burst.getContent()

		newgrb = GRB()
		newgrb.setName(burst._filename.replace("bursts/","").replace(".html",""))
		for i in range(len(burstcontent)):
			information = burstcontent[i]
		
			if re.search(patterntriggertime, information):
				tmp = information.split(" ")[-2].split(":")
				timestruct = time.struct_time((UTCNow.year, month, 06, tmp[0], tmp[1], tmp[2], 0, 0, 0))
				newgrb.setTIME(timestruct)
		
			if re.search(patternra, information) and re.search("J2000", information):
				tmp = information.replace(" ","").replace("\n","").replace(",","").replace("(J2000)","")
				ra, flag = "", False
				for i in range(len(tmp)):
					if tmp[i-1] == "{":
						flag = True
					if tmp[i] == "}":
						flag = False
					if flag:
						ra = "%s%s" % (ra, tmp[i])

				ra = ra.replace("h", "").replace("m","").replace("s","").replace("+","")
				newgrb.setRA(ra)

			if re.search(patterndec, information) and re.search("J2000", information):
                                tmp = information.replace(" ","").replace("\n","").replace(",","").replace("(J2000)","")
                                dec, flag = "", False
                                for i in range(len(tmp)):
                                        if tmp[i-1] == "{":
                                                flag = True
                                        if tmp[i] == "}":
                                                flag = False
                                        if flag:
                                                dec = "%s%s" % (dec, tmp[i])

                                dec = dec.replace("d", "").replace("\'","").replace("\"","")
				newgrb.setDEC(dec)
			if newgrb.enoughProperties():
				break

		if newgrb.enoughProperties():
			grblist.append(newgrb)

	for grb in grblist:
		print "RA:%s\nDEC:%s\nTIME:%s" % (grb.getRA(), grb.getDEC(), grb.getTIME())
		
	return grblist

if __name__ == "__main__":

	print "hawki_burstinfo.py: %s" % (datetime.datetime.today())
	main()
# Sat Dec 3 12:15:30 CET 2011
