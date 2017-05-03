#!/usr/bin/env python

import roslib
import os
import rospy
from geometry_msgs.msg import Twist,PoseStamped,Pose,Point,Quaternion, PoseWithCovarianceStamped
from actionlib_msgs.msg import GoalStatus , GoalID
from move_base_msgs.msg import MoveBaseActionResult , MoveBaseActionGoal
from nav_msgs.msg import Odometry
from std_msgs.msg import Header

#data.bumper: LEFT (0), CENTER (1), RIGHT (2)
#data.state: RELEASED(0), PRESSED(1)

goalposition = []
goalorientation = []
initposition = []
initorientation = []




def processNav(nav):
	rospy.loginfo(nav.status.text)
	os.system("ssh st@192.168.68.1 'echo "+ nav.status.text+" |festival --tts"+"'")



def processGoal(point):
	goalposition = [point.goal.target_pose.pose.position.x, point.goal.target_pose.pose.position.y, 
point.goal.target_pose.pose.position.z]
	goalorientation = [point.goal.target_pose.pose.orientation.x,
point.goal.target_pose.pose.orientation.y,
point.goal.target_pose.pose.orientation.z,
point.goal.target_pose.pose.orientation.w]
	os.system("ssh st@192.168.68.1 '"+ "echo "+"goal Set"+" |festival --tts"+"'")
	print
	print "Goal Position = ",goalposition
	print "Goal Orientation = " , goalorientation
	print 



def processVel(vel):
	angular = str(vel.angular.z)
	linear = str(vel.linear.x)
	if (vel.linear.x != 0 or vel.angular.z !=0):
		angvel = str(vel.angular.z)
		linvel = str(vel.linear.x)
		if(vel.angular.z > 0):
			angular = str(vel.angular.z)
		if(vel.angular.z < 0):
			angular = "negative" + str(vel.angular.z)
		if(vel.linear.x > 0):
			linear = str(vel.linear.x)
		if(vel.linear.x < 0):
			linear = "negative" + str(vel.linear.x)
	os.system("echo 'moving with a linear velocity of" + linear + "and an angular velocity of" + angular + "' |festival --tts")
	rospy.loginfo("linear =" + linvel)
	rospy.loginfo("angular =" + angvel)



def processInit(init):
	initposition =[init.pose.pose.position.x, init.pose.pose.position.y, init.pose.pose.position.z]
	
	initorientation =[init.pose.pose.orientation.x, init.pose.pose.orientation.y, init.pose.pose.orientation.z,init.pose.pose.orientation.w]
	
	goingback = "I am going back the my initial position"
	print ""
	print "Initial Position = ",initposition
	print "Initial Orientation = ",initorientation
	print ""
	os.system("ssh st@192.168.68.1 '"+ "echo " +"Initial Position and Orientation values recorded"+" |festival --tts"+"'")
	print "[1] --> To send me to the initial position you set"
	print "[0] --> To assign a new initial position"
	print "\n"
	inval = 1
	while(inval != 0):	
		inval = input()

		if inval == 1:
			print goingback
			print "\n"
			os.system("ssh st@192.168.68.1 '"+ "echo " +goingback+"|festival --tts"+"'")
			os.system("rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped -1 -- '{ header: {stamp: now, frame_id: 'map'}, pose: { position: {x: " + str(init.pose.pose.position.x) + ", y: "+ str(init.pose.pose.position.y)+", z: "+str(init.pose.pose.position.z) + "}, orientation: {z: "+str(init.pose.pose.orientation.z)+", w: "+ str(init.pose.pose.orientation.w)+"}}}'")

		if inval == 0:
			print "Aborting, give me a new initial position\n"
		else:
			print "Not a valid answer. Usage: [0] [1]  \n"



def listener():
	rospy.Subscriber("move_base/goal", MoveBaseActionGoal, processGoal)
	rospy.Subscriber("move_base/result", MoveBaseActionResult, processNav)
	rospy.Subscriber("initialpose", PoseWithCovarianceStamped, processInit)
	rospy.spin()




if __name__ == '__main__':
    rospy.init_node('speak')
    listener()

