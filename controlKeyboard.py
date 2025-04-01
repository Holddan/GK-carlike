#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty
import yaml


class KeyboardControl:
    def __init__(self):
        rospy.init_node('teleop_twist_keyboard')
        config_file = rospy.get_param('~keyboard_config_file', 'config/keyboard_config.yaml')
        # Load key bindings and speeds from YAML file
        config_file = rospy.get_param('~keyboard_config_file', '$(find car_like)/config/keyboard_config.yaml')
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            self.move_bindings = config.get('move_bindings', {})
            self.speed_bindings = config.get('speed_bindings', {})
            self.linear_speed = config.get('linear_speed', 0.2)
            self.angular_speed = config.get('angular_speed', 0.1)

        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.settings = termios.tcgetattr(sys.stdin)

        self.msg = """
Control Your Car!
---------------------------
Moving around:
{}

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
space key, k : force stop

anything else : stop smoothly

CTRL-C to quit
""".format('\n'.join([f"  {key}: {value}" for key, value in self.move_bindings.items()]))

        self.x = 0
        self.th = 0
        self.status = 0

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def vels(self):
        return "currently:\tspeed {}\tturn {} ".format(self.linear_speed, self.angular_speed)

    def run(self):
        print(self.msg)
        print(self.vels())
        
        print(f"Move Bindings: {self.move_bindings}")  # Thêm dòng này
        while not rospy.is_shutdown():
            key = self.getKey()
            if key in self.move_bindings:
                self.x = self.move_bindings[key][0]
                self.th = self.move_bindings[key][1]
            elif key in self.speed_bindings:
                self.linear_speed *= self.speed_bindings[key][0]
                self.angular_speed *= self.speed_bindings[key][1]
                print(self.vels())
                if (self.status == 14):
                    print(self.msg)
                self.status = (self.status + 1) % 15
            elif key == ' ' or key == 'k':
                self.x = 0
                self.th = 0
            elif (key == '\x03'):
                break
            else:
                self.x = 0
                self.th = 0
                if (key == 's'):
                    print(self.vels())
                else:
                    print("unknown key!")

            twist = Twist()
            twist.linear.x = self.x * self.linear_speed
            twist.linear.y = 0
            twist.linear.z = 0
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = self.th * self.angular_speed
            self.pub.publish(twist)

        twist = Twist()
        self.pub.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

if __name__ == "__main__":
    try:
        keyboard_control = KeyboardControl()
        keyboard_control.run()
    except Exception as e:
        print(e)
