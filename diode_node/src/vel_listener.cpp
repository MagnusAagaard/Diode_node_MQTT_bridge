#include "ros/ros.h"
#include "std_msgs/String.h"
#include "geometry_msgs/Twist.h"
#include "turtlesim/Pose.h"

//ros::Time begin;
//ros::Duration dura(0.5);
ros::Publisher diode_commands;
std_msgs::String cmd_msg;
float last_lin_vel = 0.1;
float last_ang_vel = 0.1;

/**
 * This tutorial demonstrates simple receipt of messages over the ROS system.
 */
void chatterCallback(const turtlesim::Pose::ConstPtr& msg)
{
  /*ros::Time now = ros::Time::now();
  if(now - begin > dura){
  begin = ros::Time::now();
  ROS_INFO("I heard: [something]"); , msg->data.c_str());
  ROS_INFO("I heard: %f", msg->linear.x);*/

  float lin_vel = msg->linear_velocity;
  float ang_vel = msg->angular_velocity;

  if((lin_vel == 0.0 && last_lin_vel != 0.0) || (ang_vel == 0.0 && last_ang_vel != 0.0)){
  ROS_INFO("Stop");
  cmd_msg.data = "Stop";
  diode_commands.publish(cmd_msg);
  }
  else if(lin_vel - last_lin_vel > 0.0){
  ROS_INFO("Forward");
  cmd_msg.data = "Forward";
  diode_commands.publish(cmd_msg);
  }
  else if(lin_vel - last_lin_vel < 0.0){
  ROS_INFO("Backward");
  cmd_msg.data = "Backward";
  diode_commands.publish(cmd_msg);
  }

  else if(ang_vel - last_ang_vel > 0.0){
  ROS_INFO("Left turn");
  cmd_msg.data = "Left";
  diode_commands.publish(cmd_msg);
  }
  else if(ang_vel - last_ang_vel < 0.0){
  ROS_INFO("Right turn");
  cmd_msg.data = "Right";
  diode_commands.publish(cmd_msg);
  }
  last_lin_vel = lin_vel;
  last_ang_vel = ang_vel;
}

int main(int argc, char **argv)
{
  ros::init(argc, argv, "vel_listener");
  ros::NodeHandle n;
  //begin = ros::Time::now();
  diode_commands = n.advertise<std_msgs::String>("diode_node_commands", 10);

  /**
   * The subscribe() call is how you tell ROS that you want to receive messages
   * on a given topic.  This invokes a call to the ROS
   * master node, which keeps a registry of who is publishing and who
   * is subscribing.  Messages are passed to a callback function, here
   * called chatterCallback.  subscribe() returns a Subscriber object that you
   * must hold on to until you want to unsubscribe.  When all copies of the Subscriber
   * object go out of scope, this callback will automatically be unsubscribed from
   * this topic.
   *
   * The second parameter to the subscribe() function is the size of the message
   * queue.  If messages are arriving faster than they are being processed, this
   * is the number of messages that will be buffered up before beginning to throw
   * away the oldest ones.
   */
  ros::Subscriber sub = n.subscribe("turtle1/pose", 1000, chatterCallback);

  ros::spin();

  return 0;
}
