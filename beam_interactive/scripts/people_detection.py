#!/usr/bin/env python
import sys
from tf import *
import os,roslib,rospy
from twython import Twython
from math import * 
import tf
from std_msgs.msg import *
import beam_interactive.msg
from cob_perception_msgs.msg import DetectionArray

class tweet():
	def __init__(self):
		rospy.init_node("Test")
		self.APP_KEY = 'TxOOOSqGT0QrH6r3yTHujlCDx'
		self.APP_SECRET = 'FRg5IV59j7yqHZIzSpTBDWHnOseP0brknukjJeHaUdKyHR1lRN'
		self.OAUTH_TOKEN = '816986812413513728-EF3OEuMCninLpJRkLWyctRZySG66ozT'
		self.OAUTH_TOKEN_SECRET = 'MEWgRnQkh8KGCoQCe36Z64yUfL7tFGjejyZroij2cevur'
		rospy.Subscriber("/detection_tracker/face_position_array" , DetectionArray , self.face_array)
		self.people_position = None
		self.alpha = 0
		self.detection_treshold = 0.8
		self.first_time = True
		self.face_list = list()
		self.received = False
		self.marker_pos = (0,0,0)
		self.tf_listener = TransformListener()
		self.br = tf.TransformBroadcaster()
		self.alpha_list = list()
		self.transormation = rospy.Publisher("/transform", beam_interactive.msg.people_position, queue_size=1)
		rospy.Subscriber("/Tweet_Checker" , UInt32 , self.tweet_checker)

	def run(self):
		while not rospy.is_shutdown():
			if self.received:
				twitter = Twython(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET)
				self.br.sendTransform((self.alpha, -self.face[0], 0),
				tf.transformations.quaternion_from_euler(0, 0, 0),
				rospy.Time.now(),
				"face_",
				"kinect_link")
				try:
					t = self.tf_listener.getLatestCommonTime("/map", "/face");
					(self.people_position, _) = self.tf_listener.lookupTransform('/map', '/face', t)
				except Exception as ex:
					continue
				print self.people_position
				person_position = beam_interactive.msg.people_position()
				person_position.x = self.people_position[0]
				person_position.y = self.people_position[1]
				self.transormation.publish(person_position)



	def face_array(self,data):
		if len(data.detections) > 0:
			self.received = True
			x = 0
			self.posey = 0
			appearance = False
			for x in xrange(0,len(data.detections)):
				self.face = data.detections[x].pose.pose.position.x,data.detections[x].pose.pose.position.y,data.detections[x].pose.pose.position.z
				self.alpha = sqrt(self.face[2]*self.face[2] - self.face[0]*self.face[0] )
				if self.first_time:
					self.face_list.append(self.face)
					self.alpha_list.append(self.alpha)
					self.first_time = False
					continue

				for i in xrange(0,len(self.face_list)):
					if self.distance_between(self.face,self.face_list[i]) < self.detection_treshold:
						appearance = True
				
				if not appearance:
					self.face_list.append(list(self.face))
					self.alpha_list.append(self.alpha)
					twitter = Twython(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET)
					statusupdate = "People detected at: \n"
					statusupdate += str(self.people_position)+"\n"
					twitter.update_status(status=statusupdate)
			

	def distance_between(self,pos1,pos2):
		dist = sqrt((pos1[0] - pos2[0])*(pos1[0] - pos2[0]) + (pos1[1] - pos2[1])*(pos1[1] - pos2[1])+(pos1[2] - pos2[2])*(pos1[2] - pos2[2]))
		return dist

	def tweet_checker(self,data):
		if data.data == 1 and self.received:
				twitter = Twython(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET)
				statusupdate = "People detected at: \n"
				statusupdate += str(self.people_position)+"\n"
				twitter.update_status(status=statusupdate)

if __name__ == '__main__':
		twitter = tweet()
		twitter.run()

