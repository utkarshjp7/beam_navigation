#!/usr/bin/env python
import roslib, rospy
from std_msgs.msg import UInt32

class Twitter_Checker():
	def __init__(self):
		rospy.init_node("Twitter_Checker")
		self.response = None
		self.send = UInt32()
		self.response_pub = rospy.Publisher('/Tweet_Checker', UInt32, queue_size=1)
		self.send.data = 1;

	def check(self):
		while not rospy.is_shutdown():
			self.response = raw_input("Should I tweet?\n")
			if self.response == "Y" or self.response == "Yes" or self.response == "y" or self.response == "yes":
				self.response_pub.publish(self.send)
				print self.send




if __name__ == '__main__':
	node = Twitter_Checker()
	node.check()