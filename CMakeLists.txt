cmake_minimum_required(VERSION 2.8.3)
cmake_policy(SET CMP0048 NEW)
project(car_like VERSION 1.0.0)

find_package(catkin REQUIRED COMPONENTS
   message_generation
   roscpp
   rospy
   std_msgs
   geometry_msgs
   urdf
   xacro
   message_generation
   sensor_msgs
)

catkin_package(
	CATKIN_DEPENDS
	   geometry_msgs
	   roscpp
	   rospy
	   std_msgs
)

find_package(roslaunch)

foreach(dir config launch meshes urdf)
	install(DIRECTORY ${dir}/
		DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)
