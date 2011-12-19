#!/usr/bin/python
"""Parses jochens webpage for bursts of the day."""

import datetime, sys, re
from pyweb.webclass import CopiedWebPage
from pygrb.grbclass import GRB

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
	UTCName = "%s%s%s" % (UTCNow.year-2000,UTCNow.month, UTCNow.day)
	GRBPreFix = ['grb']
	GRBEndFix = ['A', 'B', 'C', 'D', 'E', 'F']
	

	# 2.
	bursts = []
	for PreFix in GRBPreFix:
		for EndFix in GRBEndFix:
			
			GRBName = "%s%s%s" % (PreFix, UTCName, EndFix)
			Page = "%s/%s.html" % (DefaultPage, GRBName)

			newJochenPage = CopiedWebPage()
                        newJochenPage.setFileName(filename="%s.html" % GRBName)
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

		burst.parseWebPage()
		burstcontent = burst.getContent()

		newgrb = GRB()
		for i in range(len(burstcontent)):
			information = burstcontent[i]
		
			if re.search(patternra, information):
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

			if re.search(patterndec, information):
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
		print "RA:%s\nDEC:%s" % (grb.getRA(), grb.getDEC())




if __name__ == "__main__":

	print "hawki_burstinfo.py: %s" % (datetime.datetime.today())
	main()
# Sat Dec 3 12:15:30 CET 2011
