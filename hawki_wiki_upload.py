#!/usr/bin/python
"""Default python script layout."""

from lib import wikipage

__author__ = "Jonny Elliott"
__copyright__ = "Copyright 2012, adapted from V Sudilovsky 2012"
__credits__ =  ""
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Jonny Elliott"
__email__ = "jonnyelliott@mpe.mpg.de"
__status__ = "Prototype"

def main():

	wiki_url = 'https://gamma-wiki.mpe.mpg.de/GROND/'
	username = 'hawki'
	passwd = 'pwd4automation'
	pagename = 'hawkitestpage'

	wikibot = wikipage.WikiPage(wiki_url=wiki_url,pagename=pagename,username=username,password=passwd)
	wikibot.login()
	wikibot.open()
#	if not wikibot.linelist:
#		logger.info("Wiki page appears empty!, Building from scratch now")
	wikibot.linelist = ["= Page to upload remote observations of GROND =","----"]
	wikibot.attach("fc/TEST.jpg")
	wikibot.linelist.append('{{attachment:%s}}' % "TEST.jpg") #Assuming "images/..." format for filename!
	wikibot.save()
	wikibot.logout()

if __name__ == "__main__":
	main()
# Tue Jan 10 14:17:54 CET 2012
