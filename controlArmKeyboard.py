#!/usr/bin/env python3

import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import sys
import tty
import termios

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] &= ~termios.ECHO  # Tắt echo
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def send_trajectory(pub, joints, positions, time=0.5, velocities=[0.1, 0.1]):
    traj = JointTrajectory()
    traj.header.frame_id = "base_link" # Đổi frame_id thành base_link hoặc tên frame bạn muốn
    traj.header.stamp = rospy.Time.now()
    traj.joint_names = joints
    point = JointTrajectoryPoint()
    point.positions = positions
    point.velocities = velocities
    point.time_from_start = rospy.Duration(time)
    traj.points.append(point)
    pub.publish(traj)
    if time > 1:  # Chỉ sleep khi về home pose
        rospy.sleep(time)

def move_arm():
    rospy.init_node('arm_trajectory_node', anonymous=True)
    pub = rospy.Publisher('/car_like/arm_trajectory_command', JointTrajectory, queue_size=10) # Đổi topic name

    rospy.loginfo("Waiting for Gazebo...")
    rospy.wait_for_service('/gazebo/spawn_urdf_model')
    rospy.sleep(2)

    joints = ['basearm_Joint', 'arm2_Joint'] # Đổi tên khớp
    arm_base_pos, arm_pos = 0.0, 0.0 # Thay đổi giá trị khởi tạo nếu cần
    step = 0.01 # Điều chỉnh bước di chuyển cho khớp prismatic
    step_revolute = 0.05 # Điều chỉnh bước di chuyển cho khớp revolute
    limits = {'basearm_Joint': (-0.058, 0.008), 'arm2_Joint': (0.0, 3.14)} # Đổi tên khớp và giới hạn

    # Về home pose
    rospy.loginfo("Moving to home pose...")
    send_trajectory(pub, joints, [0.0, 0.0], 2.0)

    print("use 'ujik' to move , 'q' to quit") # Thay đổi hướng dẫn phím cho phù hợp với binding cũ

    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        key = get_key()
        if key == 'j': arm_base_pos = max(limits['basearm_Joint'][0], arm_base_pos - step) # Điều khiển basearm_Joint (prismatic)
        elif key == 'u': arm_base_pos = min(limits['basearm_Joint'][1], arm_base_pos + step) # Điều khiển basearm_Joint (prismatic)
        elif key == 'i': arm_pos = min(limits['arm2_Joint'][1], arm_pos + step_revolute)   # Điều khiển arm2_Joint (revolute)
        elif key == 'k': arm_pos = max(limits['arm2_Joint'][0], arm_pos - step_revolute)   # Điều khiển arm2_Joint (revolute)
        elif key == 'q':
            rospy.loginfo("Exiting...")
            break

        if key in 'juik':
            send_trajectory(pub, joints, [arm_base_pos, arm_pos])

        rate.sleep()

if __name__ == "__main__":
    try:
        move_arm()
    except rospy.ROSInterruptException:
        pass