# Date: 13.10.2011
# Author: J Elliott

import ftplib, sys
import smtplib
import imaplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64


# Usage:
Usage = """python hawki_email_send.py 'GRB Name' 'Finding Chart URL' 'OBName'
e.g. python hawki_send_email.py GRB220313A http://mpe.mpg.de/~jcg/grb220313A.jpg RRM_AUTO

Allowed OBNAME:
	AUTO
	MAN1
	MAN2
	DEFAULT: AUTO
"""

def template_email(in_FC, in_GRBName, in_OBName, in_RA, in_DEC):
	
	template_text = open("etc/rrm_template.txt", "r")
	template_msg = template_text.readlines()
	template_text.close()

	full_line = ""
	n = 0
	for line in template_msg:

		n = n + 1

		#print n, line
		if n == 76:
			# Comments
			full_line = full_line + "Comments !536870979!: finding chart: %s. We require as fast as possible (instant) access to the data. Please upload the reduced data to the following ftp as soon as possible: ftp.rzg.mpg.de/incoming/grond (user,password are anonymous).\n" % in_FC

		elif n == 19:
			# Requester
			full_line = full_line + line.replace('\n','') + " %s\n" % ("JNELLIOTT")
		elif n == 17:
			# Trigger Name
			full_line = full_line + line.replace('\n','') + "%s\n" % in_GRBName
		elif n == 27:
			# Target Name
			full_line = full_line + line.replace('\n','') + " %s\n" % in_GRBName
		elif n == 28:
			# RA
			full_line = full_line + line.replace('\n','') + " %s\n" % in_RA
		elif n == 29:
			# DEC	
			full_line = full_line + line.replace('\n','') + " %s\n" % in_DEC
		elif n == 32:
			# FC1
                        full_line = full_line + line.replace('\n','') + " %s\n" % in_FC
		elif n == 33: 
			# FC2
                        full_line = full_line + line.replace('\n','') + " %s\n" % in_FC
		elif n == 43:
			# OB Name
			full_line = full_line + line.replace('\n','') + " %s\n" % in_OBName
		elif n == 44:
			# OB Length
			full_line = full_line + line.replace('\n','') + "%s\n" % ("1.0")
		else:
			full_line = full_line + line

	file_out = "etc/%s_email_filled.txt" % (in_GRBName)
	file_open = open(file_out, "w")

	for line in range(len(full_line)):
		file_open.write('%s' % (full_line[line]))
		
	file_open.close()
	print 'Written e-mail to text file for reference'

	return(full_line)

def email_send(in_FC, in_GRBName, in_OBName, in_RA, in_DEC):

	email_user = "jonnyelliott"
	email_list = ["jonnyelliott@mpe.mpg.de"]#, "grondobs@mpe.mpg.de", "yepun@eso.org", "esoarspl@eso.org", "parmail@eso.org"]
	email_recipient = email_list[0]
	email_cc = ""
	for i in email_list[1:]:
		if email_cc == "":
			email_cc = i
		else:
			email_cc = email_cc + "," + i

	email_password = ""
	email_smtp = "smtp.mpe.mpg.de"
	email_port = 25

	# Make email
	msg = MIMEMultipart()
	msg['From'] = "jonnyelliott@mpe.mpg.de"
	msg['To'] = email_recipient
	msg['Subject'] = 'HAWK-I RRM ACTIVATION: 088.D-0678(A)'
	msg['Cc'] = email_cc

	TEMPLATE_email = template_email(in_FC, in_GRBName, in_OBName, in_RA, in_DEC)
	msg.attach(MIMEText(TEMPLATE_email))

	# Connect to email
	mailServer = smtplib.SMTP(email_smtp, email_port)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login("jonnyelliott", email_password)

	for recipient in email_list:
		mailServer.sendmail("jonnyelliott@mpe.mpg.de", recipient, msg.as_string())

	mailServer.close()
	print 'E-mails sent'

if __name__ == "__main__":
	
	try:
		in_FC = sys.argv[1]
		in_GRBName = sys.argv[2]
		in_OBName = sys.argv[3]
		in_RA = sys.argv[4]
		in_DEC = sys.argv[5]
	except:
		print 'Failed'
		sys.exit(0)

	email_send(in_FC, in_GRBName, in_OBName, in_RA, in_DEC)
