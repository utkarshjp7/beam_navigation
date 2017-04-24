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

		'''############################# SET UP INITIAL VALUES #############################'''
		self.charger_listener = TransformListener()
		self.goal_listener = TransformListener()
		self.marker_listener = TransformListener()
		self.marker_received = False
		self.now = False
		self.beam_pos = (0,0,0)
		self.beam_ori = None
		self.goal_pos = (0,0,0)
		self.goal_ori = None
		self.first = True
		self.marker_pos = (0,0,0)
		self.marker_ori = (0,0,0)
		self.pos = 0
		self.stage = 0
		self.charger_pos = (0,0,0)
		self.charger_ori = None

	def dock(self):
		rate = rospy.Rate(10.0)
		br = tf.TransformBroadcaster()
		while not rospy.is_shutdown():
			if self.marker_received:
				
				br.sendTransform((self.marker_pos[0] + cos(self.marker_pos[2])*0.385, self.marker_pos[1] + sin(self.marker_pos[2])*0.385, self.marker_pos[2]),
					tf.transformations.quaternion_from_euler(self.marker_ori[0], self.marker_ori[1], self.marker_ori[2]),
					rospy.Time.now(),
					"charger",
					"odom")

				br.sendTransform((0.7,0, 0),
					tf.transformations.quaternion_from_euler(0,0,0),
					rospy.Time.now(),
					"goal",
					"charger")
				try:
					(self.goal_pos,self.goal_ori) = self.goal_listener.lookupTransform('/odom', '/goal', rospy.Time(0))
					(self.charger_pos,self.charger_ori) = self.charger_listener.lookupTransform('/odom', '/charger', rospy.Time(0))
				except Exception as ex:
					print ex
					continue

				cmd = Twist()				
				
				if self.stage == 0:
					if self.distance_between(self.beam_pos,self.goal_pos) > 0.02:
						cmd = self.compute_control_signal(self.beam_pos,self.goal_pos)						
				#		print self.distance_between(self.goal_pos, self.beam_pos)
					else:
						self.stage = 1
				
				elif self.stage == 1:
					print self.marker_ori
					print self.beam_pos[2]
					if abs(self.marker_ori[2] - self.beam_pos[2]) > 0.01:
						cmd.angular.z = -0.2
						cmd.linear.x = 0
						print "Rotating."
					else:
						self.stage = 2
				
				elif self.stage == 2:
					if self.distance_between(self.beam_pos, self.goal_pos) < 0.55:
						cmd.linear.x = -0.2
						cmd.angular.z = 0.0
						print "Moving backwards..."
					else:
						self.stage = 3
				
				self.move_pub.publish(cmd)
				rate.sleep()

	def odom_cb(self,data):
		quaternion = (     
			0,
			0,
			data.pose.pose.orientation.z,
			data.pose.pose.orientation.w)
		yaw = tf.transformations.euler_from_quaternion(quaternion)[2]
		t = self.marker_listener.getLatestCommonTime("/odom", "/asus_link");
		position, _ = self.marker_listener.lookupTransform('/odom', '/asus_link', t) #switch arguments?
		self.beam_pos = position[0], position[1], yaw

	def pose_marker_cb(self,data):
		if len(data.markers) > 0:
			self.marker_received = True
			quaternion = (
				0,
				0,
				data.markers[0].pose.pose.orientation.z,
				data.markers[0].pose.pose.orientation.w)
			try:
				t = self.marker_listener.getLatestCommonTime("/odom", "/ar_marker_0");
				(self.marker_pos, orientation) = self.marker_listener.lookupTransform('/odom', '/ar_marker_0', t) #switch arguments?
				quaternion = (     
					0,
					0,
					orientation[2],
					orientation[3])
				eular = tf.transformations.euler_from_quaternion(quaternion)
				self.marker_ori = (eular[0], eular[1], eular[2])
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
		msg.angular.z = theta / 2
		return msg

	def distance_between(self,pos1,pos2):
		x = pos2[0] - pos1[0]
		y = pos2[1] - pos1[1]
		return sqrt(x * x + y * y)


if __name__ == '__main__':
	beam = autodock()
	beam.dock()

