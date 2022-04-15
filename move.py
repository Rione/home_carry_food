#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from camera_opencv.msg import PositionValues
import time

class Movement():
    def __init__(self):
        self.pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size = 1)
        self.sub = rospy.Subscriber('/RLDict', PositionValues, self.sub)
        self.camera_data = PositionValues()
        self.camera_data.up_down = 0
        self.camera_data.left_right = 1
        self.camera_data.far_near = 2
        self.move_on = 0   #moveOn_distance
        self.theta = 0     #rotate_theta

    def move(self):
        target_time1 = self.move_on / 10
        target_time2 = self.theta / 10
        target_time = (target_time1 + target_time2) / 2

        t = Twist()
        t.linear.x = (-1) * self.move_on * 0.2
        t.angular.z = self.theta * 20 * 3.14 / 180

        start_time = time.time()
        end_time = time.time()

        rate = rospy.Rate(50)

        while end_time - start_time <= target_time:
            self.pub.publish(t)
            end_time = time.time()
            rate.sleep()

    def sub(self, message):
        if message.left_right == 0:
            self.theta = -1
        elif message.left_right == 2:
            self.theta = 1
        else:
            self.theta = 0

        if message.far_near == 0:
            self.move_on = 0.5
        elif message.far_near == 1:
            self.move_on = 0.5
        else:
            self.move_on = 0
        
        self.move()

if __name__ == '__main__':
    rospy.init_node('move_operation')
    movement = Movement()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        rate.sleep()
