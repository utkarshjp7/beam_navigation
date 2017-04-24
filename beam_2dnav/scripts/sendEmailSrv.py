#!/usr/bin/env python
import poplib
import sys
import imaplib
import getpass
import email
import datetime
import os,rospy
import smtplib
from std_msgs.msg import String

class reader_class():
	def __init__(self):
		rospy.init_node("Beam_Email_Reader")
		self.speakpub = rospy.Publisher("/speak", String, queue_size=1)
		self.first_time = True
		self.goal = "goal"
		self.last_goal = ""
		self.old_num = []

	def process_mailbox(self,M):
		x = y = 0
		rv, data = self.M.search(None,"ALL")
		num_list = data[0].split()
		num = len(num_list)
		rv, data = self.M.fetch(num, '(RFC822)')
		if len(num_list) == len(self.old_num):
			print "NO NEW MESSAGE RECEIVED"
		else:
			len(data)
			msg = email.message_from_string(data[0][1])
			if msg['Subject'] == "Gym":
				x = 23.026607
				y = 45.96117
				self.goal = msg['Subject']
			if msg['Subject'] == "Entrance":
				x = 35.823936
				y = 120.297027
				self.goal = msg['Subject']
			if msg['Subject'] == "Lab":
				self.goal = msg['Subject']
				x = 29.851419
				y = 54.0409
			if msg['Subject'] == "SI":
				self.goal = msg['Subject']
				x = 71.390579221
				y = 131.619
			if msg['Subject'] == "MC":
				self.goal = msg['Subject']
				x = 127.1449
				y = 198.64999
			if msg['Subject'] == "SC":
				self.goal = msg['Subject']
				x = 144.9398
				y = 266.163543
			if x>0 and y >0:
				os.system("ssh st@192.168.68.1 '"+ "echo " +"I am going to the "+str(self.goal)+"|festival --tts"+"'")
				send = "rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped -1 -- '{header: {stamp: now, frame_id: "+"'map'"+"}, pose: {position: {x: "+ str(x) +" , y: "+ str(y) +"}, orientation: {w: 1.0}}}'"
				self.speakpub.publish(str(self.goal))
				os.system(send)
				self.first_time = False
				self.old_num = num_list


	def done(self):
		fromaddr = "robot";
		toaddrs  = "robot.perllab@gmail.com"
		msg = "OUT"
		username = "robot.perllab";
		password = "perlrobot123";
		server = smtplib.SMTP('smtp.gmail.com:587');
		server.starttls();
		server.login(username,password);
		server.sendmail(fromaddr, toaddrs, msg);
		server.quit();
		
	def run(self):
		while not rospy.is_shutdown():
			first_time = True
			self.M = imaplib.IMAP4_SSL('imap.gmail.com')
			try:
				self.M.login('robot.perllab@gmail.com', 'perlrobot123')
			except imaplib.IMAP4.error:
				print "LOGIN FAILED!!! "
			rv, mailboxes = self.M.list()
			rv, data = self.M.select("Inbox")
			if rv == 'OK':
				self.process_mailbox(self.M)
				self.M.close()
			self.M.logout()
		self.done()


if __name__ == '__main__':
	reader = reader_class()
	reader.run()
