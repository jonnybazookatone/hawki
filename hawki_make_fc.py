import sys, os, signal, subprocess

Usage="""This creates the finding charts for hawk-i trigger and uploads them to a webserver. Use in the following manner:
py hawki_make_fc.py RA(hhmmss.s) DEC(sddmmss.s) GRBName ERRORCircle

	e.g. python hawki_make_fc.py 021009.34 -270619.7 GRB110918A 600"""

def make_fc(in_RA, in_DEC, in_GRBName):

	# Load ds9
	d = ds9.ds9()

	# Set Image server preferences
	d.set('dsseso survey DSS2-infrared')
	d.set('dsseso size 15 15 arcmin')

	# Download the catalogued image
	image_txt = 'dsseso coord %s %s sexagesimal' % (in_RA, in_DEC)
	d.set(image_txt)

	# Image size
	x_arc = 15
	y_arc = 15

	x_width = int(d.get('fits width'))
	y_height = int(d.get('fits height'))

	x_scale = x_width/x_arc

	# Draw a circle around the GRB position
	circle_txt = 'regions command "circle %s %s 0.4\' # color = blue width = 2"' % (in_RA, in_DEC)
	d.set(circle_txt)

	# Write text at the top in the format that ESO require
	text_x, text_y = (x_width/2.0), (y_height-25)
	text_x2, text_y2 = (x_width/2.0), (y_height-75)
	text_txt = 'regions command "text %s %s \'Run ID: 088.D-0678(A), PI: JNELLIOTT\' # font = \' times 16 bold\' color = blue"' % (text_x, text_y)
	text2_txt = 'regions command "text %s %s \'Target: %s, DSS2-Infrared\'  # font = \' times 16 bold\' color = blue"' % (text_x2, text_y2, in_GRBName)
	d.set(text_txt)
	d.set(text2_txt)

	# Place a compass
	compass_x, compass_y = (x_width-10), (10)
	compass_txt = 'regions command "compass(%s,%s,100) # compass=wcs \'N\' \'E\' 1 1 color=blue width=3 font=\'times 16 bold\'"' % (compass_x, compass_y)
	d.set(compass_txt)

	# Place a rule
	ruler_x1, ruler_y1 = x_width/2.0, 10
	ruler_x2, ruler_y2 = (x_width/2.0)-(x_scale*6.1), 10
	ruler_txt = 'regions command "ruler(%s,%s,%s,%s) # ruler=arcmin color=blue width=3 font=\'times 16 bold\'"' % (ruler_x1, ruler_y1, ruler_x2, ruler_y2)
	d.set(ruler_txt)

	# Invert the colourmap
	d.set('cmap invert')

	# Save image as a JPEG format
	d.set('zscale')
	d.set('view colorbar no')
	d.set('zoom to fit')
	d.set('saveimage jpeg fc/%s.jpg 100' % (in_GRBName))

def convert_RADEC(in_RA, in_DEC):
	RA = '%s:%s:%s' % (in_RA[0:2], in_RA[2:4], in_RA[4:])
	DEC = '%s:%s:%s' % (in_DEC[0:3], in_DEC[3:5], in_DEC[5:])

	return(RA, DEC)

def upload_fc(filename):
	host = "jonnyy@codd.uwcs.co.uk:~/public_html/grbs/"
	subprocess.Popen(["scp", filename, host])

def hack_fc(in_RA, in_DEC, in_GRBName, in_ERROR):
	command = 'ds9 -dsseso survey DSS2-infrared \
-dsseso size 15 15 \
-dsseso coord %s %s \
-regions command "circle(%s,%s,%s) # color = blue width = 2" \
-regions command "text 400 850 \'Run ID: 088.D-0678(A), PI: JNELLIOTT\' # font = \'times 16 bold\' color = blue" \
-regions command "text 400 800 \'Target: %s, DSS2-Infrared\' # font = \'times 16 bold\' color = blue" \
-regions command "compass (800,10,100) # compass=wcs \'N\' \'E\' 1 1 color=blue width=3 font=\'times 16 bold\'" \
-regions command "ruler(10,100,10,500) # ruler=arcmin color=blue width=3 font=\'times 16 bold\'" \
-zscale \
-invert \
-zoom to fit \
-view colorbar no \
-saveimage jpeg fc/%s.jpg \
-exit' % (in_RA, in_DEC, in_RA, in_DEC, in_ERROR, in_GRBName, in_GRBName)

	print command	

	try:
		display = os.getenv('DISPLAY')
	except:
		display = None


	os.putenv('DISPLAY',':75')
	xvfb = subprocess.Popen(['Xvfb', ':75', '-screen', '0', '1024x768x16'])
	os.system(command)
	os.kill(xvfb.pid, signal.SIGKILL)

if __name__ == "__main__":

	try:
		in_RA = sys.argv[1]
		in_DEC = sys.argv[2]
		in_GRBName = sys.argv[3]
		in_ERROR = sys.argv[4]

	except:
		print Usage
		sys.exit(0)
		#in_RA = '021009.34'
		#in_DEC = '-270619.7'
		#in_GRBName = 'GRB110918A'


	in_RA, in_DEC = convert_RADEC(in_RA, in_DEC)
	#make_fc(in_RA, in_DEC, in_GRBName)
	hack_fc(in_RA, in_DEC, in_GRBName, in_ERROR)
	upload_fc("fc/"+in_GRBName+".jpg")
	print '---------------------------------------------'
	print 'HAWK-I RRM ACTIVATION FINDING CHART GENERATOR'
	print '---------------------------------------------'
	print ''
	print 'Finding Chart generated:'
	print 'http://jonnyy.warwickcompsoc.co.uk/grbs/%s.jpg' % (in_GRBName)

	#os.kill(xvfb.pid, signal.SIGKILL)
