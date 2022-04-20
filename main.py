#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from camera_opencv.msg import PositionValues
import time

class CarryFood():
    def __init__(self):
        #movement
        self.move_pub = rospy.Publisher('/move_stop', PositionValues, queue_size = 1)
        self.camera_sub = rospy.Subscriber('/RLDict', PositionValues, self.control_movement)
        self.stop = time.time()
        self.move_permission = 0

        #audio
        self.audio_pub = rospy.Publisher('/audio_start', String, queue_size = 1)
        self.audio_sub = rospy.Subscriber('/audio_finish', String, self.control_audio)
        self.audio_finish = 0


    
    def control_audio(self, message):
        if message.data == "ryo":
            self.audio_pub.publish("wait")
        if message.data == "ok":
            self.audio_finish = 1


    def control_movement(self, message):
        if self.move_permission == 0:
            return
        self.move_pub.publish(message)
        if message.far_near == 2:
            self.stop = time.time()
            while message.far_near == 2:
                target_time = time.time()
                if self.stop - target_time == 2:
                    self.move_allow = 0
        return


    def main(self):
        rate = rospy.Rate(10)
        self.audio_finish = 0
        self.audio_pub.publish("carry")
        while self.audio_finish != 1:
            rate.sleep()
        self.audio_finish = 0

        self.move_permission = 1
        while self.move_permission != 0:
            rate.sleep()



if __name__ == '__main__':
    rospy.init_node("main")
    carry_food = CarryFood()
    carry_food.main()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        rate.sleep()