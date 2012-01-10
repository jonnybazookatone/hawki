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

# Wikipage layout

# General Details

# Observability image

# Finding chart

def main(grbname):

	wiki_url = 'https://gamma-wiki.mpe.mpg.de/GROND/'
	username = 'hawki'
	passwd = 'pwd4automation'
	pagename = 'hawki_%s' % grbname

	fileinput = open("%s.log" % grbname, "r")
	lineinput = fileinput.readlines()
	fileinput.close()

	wikibot = wikipage.WikiPage(wiki_url=wiki_url,pagename=pagename,username=username,password=passwd)
	wikibot.login()
	wikibot.open()

	wikibot.linelist = ["= GENERAL INFORMATION ="]
	for i in lineinput:
		wikibot.linelist.append(i)

	wikibot.linelist.append("= FINDING CHART =")
	wikibot.attach("fc/%s.jpg" % grbname)
	wikibot.linelist.append('{{attachment:%s.jpg}}' % grbname) #Assuming "images/..." format for filename!

	wikibot.save()
	wikibot.logout()

if __name__ == "__main__":
	main()
# Tue Jan 10 14:17:54 CET 2012
