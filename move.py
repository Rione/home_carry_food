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

    def move_go(self):
        speed = 0.1
        target_time = self.move_on / 10

        t = Twist()
        t.linear.x = (-1) * self.move_on * speed
        t.angular.z = 0

        start_time = time.time()
        end_time = time.time()

        rate = rospy.Rate(50)

        while end_time - start_time <= target_time:
            self.pub.publish(t)
            end_time = time.time()
            rate.sleep()

    def move_turn(self):
        speed = 20
        target_time = self.theta / speed

        t = Twist()
        t.linear.x = 0
        t.angular.z = self.theta*speed*3.14/180

        start_time = time.time()
        end_time = time.time()

        rate = rospy.Rate(10)

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
        print("me " + str(message.left_right))
        print("tu " + str(self.theta))
        self.move_turn()

        if message.far_near == 0:
            self.move_on = 2
        elif message.far_near == 1:
            self.move_on = 1
        else:
            self.move_on = 0
        print("go " + str(self.move_on))
        self.move_go()

if __name__ == '__main__':
    rospy.init_node('move_operation')
    movement = Movement()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        rate.sleep()
