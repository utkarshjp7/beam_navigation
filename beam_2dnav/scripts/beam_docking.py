'''
When beam first sees the charger, it creates two transform objects which are 
child to /odom. After that the tracking does its job.
'''
'''
Need to create the tf objects when the robot last sees the charger ##########
'''
#!/usr/bin/env python
import time, random, rospy, roslib, tf
import numpy as np
from math import *
from geometry_msgs.msg import Twist
from tf import *
from std_msgs.msg import Float32
from ar_track_alvar_msgs.msg import AlvarMarkers
from nav_msgs.msg import Odometry

class autodock():
	def __init__(self):
		rospy.init_node("Beam_Charge")
		self.move_pub = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)
		rospy.Subscriber("/ar_pose_marker" , AlvarMarkers , self.pose_marker_cb)
		rospy.Subscriber("/odom" , Odometry, self.odom_cb)

		self.tf_listener = TransformListener()
		self.marker_received = False
		self.beam_pos = (0,0,0)
		self.beam_ori = None
		self.goal_pos = (0,0,0)
		self.goal_ori = None
		self.marker_pos = (0,0,0)
		self.marker_ori = (0,0,0)
		self.stage = 0
		self.charger_pos = (0,0,0)

	def dock(self):
		br = tf.TransformBroadcaster()
		while not rospy.is_shutdown():
			if self.marker_received:
				if not self.stage == 1:
					self.charger_pos = (self.marker_pos[0] + cos(self.marker_pos[2])*0.1, self.marker_pos[1] + sin(self.marker_pos[0])*0.1, self.marker_pos[2])				
				br.sendTransform((self.charger_pos[0], self.charger_pos[1], self.charger_pos[2]),
					tf.transformations.quaternion_from_euler(self.marker_ori[0], self.marker_ori[1], self.marker_ori[2]),
					rospy.Time.now(),
					"charger",
					"odom")

				br.sendTransform((0.9,0, 0),
					tf.transformations.quaternion_from_euler(0,0,0),
					rospy.Time.now(),
					"goal",
					"charger")
				try:
					(self.goal_pos,self.goal_ori) = self.tf_listener.lookupTransform('/odom', '/goal', rospy.Time(0))
				except Exception as ex:
					continue

				cmd = Twist()				
				
				if self.stage == 0:
					if self.distance_between(self.beam_pos,self.goal_pos) > 0.05:
						cmd = self.compute_control_signal(self.beam_pos,self.goal_pos)						
					else:
						self.stage = 1
				
				elif self.stage == 1:
					if abs(self.marker_ori[2] - self.beam_pos[2]) > 0.05:
						cmd.angular.z = -0.4
						cmd.linear.x = 0
					else:
						self.beam_pos = self.goal_pos
						self.stage = 2
						
				elif self.stage == 2:
					if self.distance_between(self.beam_pos, self.charger_pos) > 0.54:
						cmd.linear.x = -0.2
						cmd.angular.z = 0.0
					else:
						self.stage = 3
				print self.distance_between(self.beam_pos, self.charger_pos)		###################
				self.move_pub.publish(cmd)

	def odom_cb(self,data):
		quaternion = (     
			0,
			0,
			data.pose.pose.orientation.z,
			data.pose.pose.orientation.w)
		yaw = tf.transformations.euler_from_quaternion(quaternion)[2]
		t = self.tf_listener.getLatestCommonTime("/odom", "/asus_link");
		position, _ = self.tf_listener.lookupTransform('/odom', '/asus_link', t) #switch arguments?
		self.beam_pos = position[0], position[1], yaw

	def pose_marker_cb(self,data):
		if len(data.markers) > 0:
			self.marker_received = True
			try:
				t = self.tf_listener.getLatestCommonTime("/odom", "/ar_marker_0");
				(self.marker_pos, orientation) = self.tf_listener.lookupTransform('/odom', '/ar_marker_0', t)
				quaternion = (     
					0,
					0,
					orientation[2],
					orientation[3])
				euler = tf.transformations.euler_from_quaternion(quaternion)
				self.marker_ori = (euler[0], euler[1], euler[2])
			except Exception as ex:
				print ex
		
	def compute_control_signal(self, posb, poso):
		beam_point = (posb[0], posb[1])
		object_point = (poso[0], poso[1])
		vectorHR = np.subtract(object_point, beam_point) 
		angleHR = np.arctan2(vectorHR[1], vectorHR[0])
		theta = angleHR - posb[2]
		if theta < -np.pi:
			theta += 2*np.pi   
		if theta > np.pi:
			theta -=  2*np.pi 
		msg = Twist()
		msg.linear.x = 0.2
		msg.angular.z = theta 
		return msg

	def distance_between(self,pos1,pos2):
		x = pos2[0] - pos1[0]
		y = pos2[1] - pos1[1]
		return sqrt(x * x + y * y)

if __name__ == '__main__':
	beam = autodock()
	beam.dock()

