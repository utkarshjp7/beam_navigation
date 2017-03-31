#!/usr/bin/env python
import poplib
import sys
import imaplib
import getpass
import email
import datetime
import os,rospy
import smtplib

class reader_class():
	def __init__(self):
		rospy.init_node("Beam_Email_Reader")
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
				x = 76.600440979
				y = 11.0695152283
				self.goal = msg['Subject']
			if msg['Subject'] == "Entrance":
				x = 3.3780708313
				y = 16.2051582336
				self.goal = msg['Subject']
			if msg['Subject'] == "Elevators":
				self.goal = msg['Subject']
				x = 51.1922950745
				y = 9.5178546955
			if x>0 and y >0:
				os.system("ssh st@192.168.68.1 '"+ "echo " +"I am going to the "+str(self.goal)+"|festival --tts"+"'")
				send = "rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped -1 -- '{header: {stamp: now, frame_id: "+"map"+"}, pose: {position: {x: "+ str(x) +" , y: "+ str(y) +"}, orientation: {w: 1.0}}}'"
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
