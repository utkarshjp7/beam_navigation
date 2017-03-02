#include<ros/ros.h>
#include<iostream>

using namespace std;

int main(int argc, char** argv)
{
  ros::init(argc, argv, "init_connection");
  ros::NodeHandle n;
 
  string beam_ip, user, pass, cmd;

  n.getParam("/beam_ip", beam_ip);
  n.getParam("/user", user);

 //restart rosbeam-bridge
  cmd = "ssh " + user + "@" + beam_ip + " \"pkill rosbeam-bridge ; rosbeam-bridge.sh\"";
  system(cmd.c_str());    

}



