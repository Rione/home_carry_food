#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
import time

class Movement():
    def __init__(self):
        self.pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size = 1)

    def move_right(self):
        theta = 1
        speed = 20
        target_time = theta / speed

        t = Twist()
        t.linear.x = 0
        t.angular.z = (-1)*speed*3.14/180

        start_time = time.time()
        end_time = time.time()

        rate = rospy.Rate(10)

        while end_time - start_time <= target_time:
            self.pub.publish(t)
            end_time = time.time()
            rate.sleep()

    def move_left(self):
        theta = 1
        speed = 20
        target_time = theta / speed

        t = Twist()
        t.linear.x = 0
        t.angular.z = speed*3.14/180

        start_time = time.time()
        end_time = time.time()

        rate = rospy.Rate(10)

        while end_time - start_time <= target_time:
            self.pub.publish(t)
            end_time = time.time()
            rate.sleep()

    def sub(self, message):
        if message.data == 0:
            self.move_right()
        elif message.data == 2:
            self.move_left()
        #elif message.data == 1:
            #stop

if __name__ == '__main__':
    rospy.init_node('move_operation')
    movement = Movement()
    sub = rospy.Subscriber('/RLDict', Int32, movement.sub)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        rate.sleep()
