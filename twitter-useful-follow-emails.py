from imaplib import *
import smtplib
from email.mime.text import MIMEText
import unicodedata
import time
#import twitter.api
#api = twitter.api.Twitter()
#NOTE: following line requires 'python-twitter', not 'twitter' (look up the difference in pypi)
import twitter
api = twitter.Api()
from email.Parser import Parser
import datetime, time, email, email.Utils
import re
from BeautifulSoup import BeautifulSoup
 
'''
headers:
from	Twitter <twitter-follow-gameguy43=gmail.com@postmaster.twitter.com>
reply-to	noreply@postmaster.twitter.com
to	gameguy43@gmail.com
date	Sat, Dec 19, 2009 at 8:41 AM
subject	LisetteHuffman is now following you on Twitter!
mailed-by	postmaster.twitter.com
signed-by	twitter.com

'''

#CONSTANTS
#grabbing the original twitter emails
ORIG_EMAIL_SERVER = 'imap.gmail.com'
ORIG_EMAIL_PORT = 993
ORIG_EMAIL_USERNAME = 'username@gmail.com'
ORIG_EMAIL_PASSWORD = 'password'
ORIG_EMAIL_FOLDER = 'twitter-newfollower-unprocessed'
ORIG_EMAIL_FROM = ''
ORIG_EMAIL_METHOD = IMAP4_SSL
#composing and sending the newer, better email
NEW_EMAIL_TO = 'username@gmail.com'
NEW_EMAIL_FROM = 'name@emailaddress.com'
NEW_EMAIL_SUBJECT = 'TF: %s'
NEW_EMAIL_BODY = u'%(followerName)s is now following you on twitter.\nzer statuses:\n%(followerStatuses)s'
NEW_EMAIL_SMTP_SERVER = 'smtp.gmail.com'
NEW_EMAIL_SMTP_PORT = 587
NEW_EMAIL_SMTP_USERNAME = ORIG_EMAIL_USERNAME
NEW_EMAIL_SMTP_PASS = ORIG_EMAIL_PASSWORD

#ONLY PARKER USES THESE; OTHERS SHOULD COMMENT OUT THIS LINE
from parkerCredentials import *

print ORIG_EMAIL_PASSWORD


# Connect to email server
server = ORIG_EMAIL_METHOD(ORIG_EMAIL_SERVER, ORIG_EMAIL_PORT)
server.login(ORIG_EMAIL_USERNAME, ORIG_EMAIL_PASSWORD)
r = server.select(ORIG_EMAIL_FOLDER)
 
# Find only new mail (i.e. new direct messages)
r, data = server.search(None,'(FROM "' + ORIG_EMAIL_FROM + '")') 

i = 0

# If there are new direct messages:
if len(data[0]) > 0:
 
    p = Parser()
 
    # Loop through new emails
    for num in data[0].split():
	i+=1
	# Get body of email sent by Twitter
	r, data = server.fetch(num, '(UID BODY[TEXT])')
	emailBody = data[0][1]
	# delete the original email
	server.store(num, "+FLAGS", '\\Deleted')
	server.expunge()
	# an index in the string which is after where the follower's name appears and on the same line
	AlmostThere = emailBody.find('is now following your tweets on Twitter.')
	follower_username = emailBody[:AlmostThere].rpartition('(')[2].rpartition(')')[0]
	print follower_username

	#try:
	statuses = api.GetUserTimeline(follower_username)
	[s.text for s in statuses]
	statuses_emailReady = ''
	for s in statuses:
		statuses_emailReady += s.text + "\n========\n"
		print s.text
	print statuses_emailReady
	emailBody = NEW_EMAIL_BODY % {'followerName': follower_username, 'followerStatuses': statuses_emailReady}
	newEmail = MIMEText(unicodedata.normalize('NFKD', emailBody).encode('ascii', 'ignore'))
	newEmail['Subject'] = NEW_EMAIL_SUBJECT % follower_username
	newEmail['From'] = NEW_EMAIL_FROM
	newEmail['To'] = NEW_EMAIL_TO
	s = smtplib.SMTP(NEW_EMAIL_SMTP_SERVER, NEW_EMAIL_SMTP_PORT)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(NEW_EMAIL_SMTP_USERNAME, NEW_EMAIL_SMTP_PASS)
	s.sendmail(NEW_EMAIL_FROM, NEW_EMAIL_TO, newEmail.as_string())
	s.quit()



	#except:
		#print "well, i couldn't get this person's timeline.  they probably were removed for weird activity."
	# Do something with the twitter direct message...
	# Parse it...
	# Store it in a database?...
print i
# Logout of email server
server.logout()

