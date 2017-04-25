#!/usr/bin/env python
import sys
from tf import *
import os,roslib,rospy
from twython import Twython
from math import * 
import tf
from std_msgs.msg import Float64, UInt32
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
				self.posey = 0
				self.received = False
				self.n = None
				self.angley = 0
				self.marker_pos = (0,0,0)
				self.tf_listener = TransformListener()
				self.br = tf.TransformBroadcaster()
				self.puby = rospy.Publisher('/tilt_angle',Float64,queue_size=1)
				rospy.Subscriber("/Tweet_Checker" , UInt32 , self.tweet_checker)

		def run(self):
				while not rospy.is_shutdown():
					if self.received:
						twitter = Twython(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET)
						self.br.sendTransform((self.alpha, -self.face[0], 0),
						tf.transformations.quaternion_from_euler(0, 0, 0),
						rospy.Time.now(),
						"face",
						"kinect_link")
						try:
							t = self.tf_listener.getLatestCommonTime("/map", "/face");
							(self.people_position, _) = self.tf_listener.lookupTransform('/map', '/face', t)
						except Exception as ex:
							continue
#						statusupdate = "I saw a person at  " + str(self.marker_pos)
#						twitter.update_status(status=statusupdate)


		def face_array(self,data):

			self.face = data.detections[0].pose.pose.position.x,data.detections[0].pose.pose.position.y,data.detections[0].pose.pose.position.z
			self.alpha = sqrt(self.face[2]*self.face[2] - self.face[0]*self.face[0] )
			if len(data.detections) > 0:
				self.received = True
				x = 0
				self.posey = 0
				for x in xrange(0,len(data.detections)):
					self.posey += (data.detections[x].mask.roi.y)/(x+1)   
				if self.posey < 200:
					if(self.angley<29):
						self.angley += 1
				if self.posey > 290:
					if(self.angley>-29):
						self.angley -= 1	
				print self.posey
				self.puby.publish(self.angley)



		def tweet_checker(self,data):
				if data.data == 1 and self.received:
						twitter = Twython(self.APP_KEY, self.APP_SECRET, self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET)
						statusupdate = "People detected at: \n"
						#for x in xrange(0,self.length):
						statusupdate += str(self.face)+"\n"
						twitter.update_status(status=statusupdate)

if __name__ == '__main__':
		twitter = tweet()
		twitter.run()

