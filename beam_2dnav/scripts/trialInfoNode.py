#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from std_msgs.msg import *
from nav_msgs.msg import Odometry
from datetime import datetime
import psycopg2

class trialInfoLoader:

	def __init__(self):
		rospy.init_node("trial_info_loader");
		connect_str = "dbname='beam_navigation' user='beam' host='localhost' password='beam'";
		self.conn = psycopg2.connect(connect_str);

		rospy.Subscriber("/cmd_vel", Twist, self._velocityCb);
		rospy.Subscriber("/trans_dist", Float32, self._distanceCb);
		rospy.Subscriber("/initialpose", PoseWithCovarianceStamped, self._initPoseCb);
		rospy.Subscriber("/odom", Odometry, self._odomCb);
	
		self._tid = None;
		self._init_pose = None;
		self._start_time = None;
		self._distance_travelled = None;
		self._trial_initialized = None;
		self._lastCmdVelMsgTime = None;

	def _velocityCb(self, msg):
		self._lastCmdVelMsgTime = datetime.now();
		if not self._trial_initialized:
			self._trial_initialized = True;
			self._start_time = datetime.now();			
			self._distance_travelled = 0.0;
			
			insert_start_time = "INSERT INTO trial_logs(start_time, init_pos_x, init_pos_y) VALUES ('{0}', {1}, {2})".format(str(self._start_time), self._init_pose[0], self._init_pose[1]);
			select_latest_tid = "SELECT id FROM trial_logs ORDER BY start_time DESC LIMIT 1";
			self._execute(insert_start_time, False);
			self._tid = self._execute(select_latest_tid, True);
			self._tid = self._tid[0][0];
		else:
			t = (datetime.now() - self._start_time).total_seconds();
			avg_speed = self._distance_travelled / t ;
			update_avg_speed = "UPDATE trial_logs SET average_speed={0} WHERE id={1}".format(avg_speed, self._tid);
			update_final_pose = "UPDATE trial_logs SET final_pos_x={0}, final_pos_y={1} WHERE id={2}".format(self._current_pos[0], self._current_pos[1], self._tid);
			update_end_time = "UPDATE trial_logs SET end_time='{0}' WHERE id={1}".format(str(datetime.now()), self._tid);
		#	print update_final_pose;
		#	print update_end_time;
			self._execute(update_final_pose, False);
			self._execute(update_end_time, False);
			self._execute(update_avg_speed, False);

	def _distanceCb(self, msg):
		if self._trial_initialized and (datetime.now() - self._lastCmdVelMsgTime).total_seconds() < 1.0:
			self._distance_travelled += msg.data;
			update_distance_travelled = "UPDATE trial_logs SET distance_travelled={0} WHERE id={1}".format(self._distance_travelled, self._tid);
		#	print update_distance_travelled;
			self._execute(update_distance_travelled, False);

	def _initPoseCb(self, msg):
		self._trial_initialized = False;
		self._init_pose = (msg.pose.pose.position.x, msg.pose.pose.position.y);
		
	def _odomCb(self, msg):
		if self._trial_initialized:
			self._current_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y);

	def _execute(self, sql, fetch):
		result = None;
		cursor = self.conn.cursor();
		try:
			cursor.execute(sql);
		except psycopg2.Error as e:
			print "Database error occured while executing '",sql,"'";
			print e.diag.message_primary;		
		if fetch:
			result = cursor.fetchall();
		self.conn.commit();
		cursor.close();
		return result;

	def spin(self):
        	r = rospy.Rate(30);
        	while not rospy.is_shutdown():
            		r.sleep();

if __name__ == '__main__':
	trial_info_loader = trialInfoLoader();
	trial_info_loader.spin();
