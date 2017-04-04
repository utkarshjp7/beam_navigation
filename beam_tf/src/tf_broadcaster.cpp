#include <ros/ros.h>
#include <tf/transform_broadcaster.h>

int main(int argc, char** argv){
  ros::init(argc, argv, "beam_tf_publisher");
  ros::NodeHandle n;

  ros::Rate r(30);

  tf::TransformBroadcaster broadcaster;

  while(n.ok()){
    broadcaster.sendTransform(
      tf::StampedTransform(
        tf::Transform(tf::Quaternion(0, 0, 0, 1), tf::Vector3(0.1778, 0.0, 0.0)),
        ros::Time::now(),"/base_link", "/asus_link"));
    r.sleep();
  }
}
