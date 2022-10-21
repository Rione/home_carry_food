#!/usr/bin/env python

import rospy
import sys
from std_msgs.msg import String
from carry_food.msg import PositionValues
import time

class CarryFood():
    def __init__(self):
        #movement
        self.move_pub = rospy.Publisher('/move_stop', PositionValues, queue_size = 1)  #to /move
        self.camera_sub = rospy.Subscriber('/RLDict', PositionValues, self.control_movement)  #from /Camera
        self.stop = 0   #move stop counter
        self.move_permission = 0  #move permission 0 = False, 1 = True
        self.move_turn = 0  #turn 180 angul

        #audio
        self.audio_pub = rospy.Publisher('/audio_start', String, queue_size = 1, latch = True)  #to /audio
        self.audio_sub = rospy.Subscriber('/audio_finish', String, self.control_audio)  #from /audio
        self.audio_finish = 0  #0 = False, 1 = True
    
    def control_audio(self, message):
        if message.data == "ryo":    #audio accept
            self.audio_pub.publish("wait")
        if message.data == "ok":
            self.audio_finish = 1
        return 0

    def control_movement(self, message):
        if self.move_permission == 0:
            return 0
        
        if self.move_turn == 1:   #turn 180 angul
            message.up_down = 180
            self.move_pub.publish(message)
            self.move_turn = 0
            self.move_permission = 0
            return 0

        self.move_pub.publish(message)
        if message.far_near == 2:   #good distance
            self.stop += 1
        else:
            self.stop = 0
        
        if self.stop == 10 *2:  #keeped 2 minutes
            self.move_permission = 0
        
        return 0

    def main(self):
        rate = rospy.Rate(10)
        time.sleep(3)

        #audio start listening to the word, "carry food"
        self.audio_finish = 0
        self.audio_pub.publish("carry")
        while self.audio_finish == 0:
            rate.sleep()
        self.audio_finish = 0

        #turn_180
        self.move_turn = 1
        self.move_permission = 1
        while True:
            topic = rospy.wait_for_message('/turn_finish', String)
            if topic.data == "finish":
                break

        #move to the person who ordered
        self.move_permission = 1
        self.move_stop = 0
        while self.move_permission == 1:
            rate.sleep()
        
        #audio start listening to the word, "i received the food"
        self.audio_finish = 0
        self.audio_pub.publish("stand-by")
        while self.audio_finish == 0:
            rate.sleep()
        self.audio_finish = 0

        #turn_180
        self.turn_finish = 0
        self.move_turn = 1
        self.move_permission = 1
        while True:
            topic = rospy.wait_for_message('/turn_finish', String)
            if topic.data == "finish":
                break
        
        #move to the original person
        self.move_permission = 1
        self.move_stop = 0
        while self.move_permission == 1:
            rate.sleep()
        
        sys.exit()


if __name__ == '__main__':
    rospy.init_node("main")
    carry_food = CarryFood()
    carry_food.main()