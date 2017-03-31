import rospy
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from std_msgs.msg import *
from datetime import datetime
import psycopg2

class trialInfoLoader:

	def __init__(self):
		rospy.init_node("trial_info_loader")

		connect_str = "dbname='beam_navigation' user='beam' host='localhost' password='beam'"
		self.conn = psycopg2.connect(connect_str)

		self._rate = rospy.get_param("diff_tf/rate", 30)
		self.Subscriber("/cmd_vel", Twist, self._velocityCb)
		self.Subscriber("/trans_dist", Float32, self._distanceCb)
		self.Subscriber("/initial_pose", Float32, self._initPoseCb)
	
		self._trial = None
		self._trial_info = None
		self._init_trial = False
		self._end_trial = False

	def _velocityCb(selfi, msg):
		if msg.linear.x != 0 or msg.angular.z != 0:
			self._init_trial = True
			self._trial = trial(self.conn, datetime.now())
			self._trial_info = trial_info(self._tril.tid)
			self._trial_info.init_pose = self._init_pose

	def _distanceCb(self, msg):
		if self._init_trial:
			self._tril_info.distance_travelled += msg.data

	def _initPoseCb(self, msg):
		self._init_pose = (msg.pose.pose.position.x, msg.pose.pose.position.y)
			

class trial:
	def __init__(self, conn, start_time):
		self.start_time = start_time
		cursor = conn.cursor()
		insert_str = "INSERT INTO trials(start_time) VALUES ('" + str(start_time) + "')"
		cursor.execute(insert_str);
		cursor.execute("""SELECT TOP 1 id FROM trials ORDER BY start_time DESC """)
		self.tid = cursor.fetchall()
		conn.commit()
		cursor.close()

class trial_info:
	def __init__(self, tid):
		self.tid = tid
		self.distance_travelled = 0.0
		self.average_speed = 0.0
		self.init_pose = None

if __name__ == '__main__':
    diffTf = DiffTf()
    diffTf.spin()
