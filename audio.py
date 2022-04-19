#!/usr/bin/env python


import rospy
from std_msgs.msg import String
import os
from pocketsphinx import LiveSpeech
import sys
sys.path.append('audio_src/')
from module import module_pico
from module import module_beep

oa_dict = {}  #order and answer
with open('audio_src/carry_food.txt', 'r') as f:
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

class OandA():
    def __init__(self):
        self.pub = rospy.Publisher('/audio_fin', String, queue_size = 1)
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
        self.setup_live_speech(False, dic_path, gram_path, 1e-20)

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


    # setup livespeech
    def setup_live_speech(self, TF, dict_path, jsgf_path, kws_threshold):

        ###############
        #
        # use this module to set live espeech parameter
        #
        # param >> lm: False >> means useing own dict and gram
        # param >> dict_path: ~.dict file's path
        # param >> jsgf_path: ~.gram file's path
        # param >> kws_threshold: mean's confidence (1e-)
        #
        # return >> None
        #
        ###############

        global live_speech
        live_speech = LiveSpeech(lm=TF,
                                dic=dict_path,
                                jsgf=jsgf_path,
                                kws_threshold=kws_threshold
                                )

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
                self.pub("ok")
                break
            print("----------------------------------")
        
        module_pico.speak(oa_dict[order])
        print("----------------------------------")

    def cb(message):
        if message.data == "carry" or message.data == "stand-by":
            self.main(message.data)

if __name__ == '__main__':
    rospy.init_node('audio')
    OrderAndAnswer = OandA()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        rate.sleep()