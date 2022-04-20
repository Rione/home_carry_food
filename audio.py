#!/usr/bin/env python


import rospy
from std_msgs.msg import String
import os
from pocketsphinx import LiveSpeech
import sys
sys.dont_write_bytecode = True
sys.path.append('/home/ri-one/catkin_ws/src/carry_food/audio_src/')
from module import module_pico
from module import module_beep

oa_dict = {}  #order and answer
with open('/home/ri-one/catkin_ws/src/carry_food/audio_src/carry_food.txt', 'r') as f:
    oa_list = f.readlines()
    #print("----------order list-----------")
    for oa in oa_list:
        oa = oa.rstrip().split(',')
        oa_dict[str.lower(oa[0])] = oa[1]
        #print(str.lower(oa[0]))
    #print("----------order list-----------\n")
# Define path
file_path = os.path.abspath(__file__)
dic_path = file_path.replace(
    '/audio.py', '/audio_src/carry_food.dict')
gram_path = file_path.replace(
    '/audio.py', '/audio_src/carry_food.gram')

live_speech = LiveSpeech(lm=False, dic=dic_path, jsgf=gram_path, kws_threshold=1e-20)

class OandA():
    def __init__(self):
        self.pub = rospy.Publisher('/audio_finish', String, queue_size = 1)
        self.sub = rospy.Subscriber('/audio_start', String, self.cb)

    def recognition(self):

        ###############
        #
        # test pocketsphinx with dictionary
        #
        # param >> None
        #
        # return >> None
        #
        ###############

        global live_speech
        print('[*] START RECOGNITION')

        module_beep.beep()
        for phrase in live_speech:
            noise_words = self.read_noise_word(gram_path)
            if str(phrase) == "":
                pass
            elif str(phrase) not in noise_words:
                return str(phrase)

            # noise
            else:
                #print(".*._noise_.*.")
                pass

    def read_noise_word(self, gram_path):

        ###############
        #
        # use this module to put noise to list
        #
        # param >> gram_path: grammer's path which you want to read noises
        #
        # return >> words: list in noises
        #
        ###############

        words = []
        with open(gram_path) as f:
            for line in f.readlines():
                if "<noise>" not in line:
                    continue
                if "<rule>" in line:
                    continue
                line = line.replace("<noise>", "").replace(
                        " = ", "").replace("\n", "").replace(";", "")
                words = line.split(" | ")
        return words

    def main(self, message):
        while True:
            order = self.recognition()
            print("recognition: ", order)
            if (message == "carry" and order == "carry food") or \
                (message == "stand-by" and order == "i received the food"):
                self.pub.publish("ok")
                break
            print("----------------------------------")
        
        module_pico.speak(oa_dict[order])
        print("----------listening fin----------")

    def cb(self, message):
        if message.data == "carry" or message.data == "stand-by":
            self.pub.publish("ryo")
            self.main(message.data)

if __name__ == '__main__':
    rospy.init_node('audio')
    OrderAndAnswer = OandA()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        try:
            rate.sleep()
        except:
            sys.exit()