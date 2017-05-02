#include <ros/ros.h>
#include <tf/transform_broadcaster.h>

int main(int argc, char** argv){
	ros::init(argc, argv, "beam_tf_publisher");
	ros::NodeHandle n;

	ros::Rate r(30);

	tf::TransformBroadcaster broadcaster;

	float ori = -500;
	while(n.ok()){
		broadcaster.sendTransform(
			tf::StampedTransform(
				tf::Transform(tf::Quaternion(0, 0, 0, 1), tf::Vector3(0.1778, 0.0, 0.1395)),
				ros::Time::now(),"/base_link", "/asus_link"));
		broadcaster.sendTransform(
			tf::StampedTransform(
				tf::Transform(tf::Quaternion(0, 0, 0, 1), tf::Vector3(-0.1478, 0.0, 1.3208)),
				ros::Time::now(),"/base_link", "/kinect_link"));
		r.sleep();
	}
}
//-0.1478
