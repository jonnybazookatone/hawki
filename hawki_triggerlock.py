#!/usr/bin/python
"""Default python script layout."""

import sys
import os
import glob

from hawki_mounted import mounted 
from hawki_schedule import main as observability 

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2011"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"

def main():

	# 2. MOUNTED
	#
	# Check old file exists, rrmLog_WebStatus.html
		
	filename = "%s/%s" % (sys.path[0], "rrmLog_WebStatus.html")
	if glob.glob(filename):
		os.remove(filename)

	Mounted = mounted(verbose=True)

	# 3. OBSERVABLE
	#
	
	Observability = observability(RA, DEC, EQUINOX)

if __name__ == "__main__":
	main(RA, DEC, EQUINOX, NAME)
# Tue Dec 20 18:53:04 CET 2011
