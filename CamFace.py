#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import rospy
from camera_opencv.msg import PositionValues
import time

class CamFaceDict():

    def __init__(self):
        self.a = 0
        self.pub = rospy.Publisher('/RLDict', PositionValues, queue_size=1) #左右の向きを保持する
        self.position = PositionValues()
        self.position.up_down = 0
        self.position.left_right = 1
        self.position.far_near = 2
        self.change_value = [1, 0, 2]
        self.change_time_1 = time.time()
        self.change_time_2 = time.time()

    def FaceShow(self, FaceCascade, FaceImg):
    
        #capture = cv2.VideoCapture(0)
        Wpos = 1 #0:左、1:中央、2:右
        Hpos = 0 #0:上、1:中央、2:右
        Dpos = 4 #0:遠い、1:もうちょい、2:良い、3:近すぎる、4:検出なし
        self.change_value[0] = Wpos
        self.change_value[1] = Hpos
        self.change_value[2] = Dpos

        FaceWHDpos = np.zeros(3)

        # カスケード分類器のxmlファイルを取得する。
        face_cascade_path = FaceCascade
    
        # カスケード分類器を作成 
        face_cascade = cv2.CascadeClassifier(face_cascade_path) 

        # グレースケール化 
        Img_gray = cv2.cvtColor(FaceImg, cv2.COLOR_BGR2GRAY) 

        # cv2で開くため不要
        # 出力結果用にコピー & RGB化 
        #Img = cv2.cvtColor(Img, cv2.COLOR_BGR2RGB) 
        #囲む色 
        color = (0, 255, 0) 
        #顔を検知 
    
        faces = face_cascade.detectMultiScale(Img_gray) 
    
        height, width, channels = FaceImg.shape[:3] #配列の成分を取得

        for (x,y,w,h) in faces: 
        # 検知した顔を矩形で囲む 
            cv2.rectangle(FaceImg,(x,y),(x+w,y+h),(255,0,0),2) 
            roi_color = FaceImg[y:y+h, x:x+w] 
            #print("顔は (" + str(x) + "," + str(y) + ") と " + "(" + str(x+w) + "," + str(y+h) + ") にある。")

            #顔が左右のいずれに映るか
            if x + w / 2 < width * 2 / 5:
                #print("顔が右にあるが反転し左に映る。")
                Wpos = 2

            elif x + w / 2 < width * 3 / 5 and x + w / 2 >= width * 2 / 5:
                #print("顔が左右中央にある。")
                Wpos = 1

            elif x + w / 2 < width * 5 / 5:
                #print("顔が左にあるが反転し右に映る。")
                Wpos = 0
            
            else:
                Wpos = 1

            #顔が上下のいずれに映るか
            if y + h / 2 < height * (3 / 2) / 3:
                #print("顔が上にある。")
                Hpos = 0

            elif y + h / 2 < height * 2 / 3 and y + h / 2 >= height * (3 / 2) / 3:
                #print("顔が上下中央にある。")
                Hpos = 1

            else:
                #print("顔が下にある。")
                Hpos = 2

            #顔が遠近のいずれに映るか
            if w < 80 or h < 80:
                Dpos = 0 #遠いとき速くしようと思ったけど、料理を運ぶために速度変化は無い方が良いかなと思ったため1と0で速度変化はなし。

            elif (w >= 80 and w < 150) or (h >= 80 and h < 150):
                Dpos = 1 
        
            elif (w >= 150 and w < 230) or (h >= 150 and h < 230):
                Dpos = 2 # 

            elif (w >= 230) or (h >= 230):
                Dpos = 3
            
            else:
                Dpos = 2

            #print("幅は、" + str(w) + "で 高さは" + str(h) + "です。")

        FaceWHDpos[0] = Hpos #0番目の要素が上下の位置を保持
        FaceWHDpos[1] = Wpos #1番目の要素が左右の位置を保持
        FaceWHDpos[2] = Dpos #2番目の要素が遠近の位置を保持

        #一瞬消える青枠の情報を整備（調整中で汚いコードです）
        self.change_time_1 = time.time()
        if (self.change_value[0] != FaceWHDpos[0]) or \
           (self.change_value[1] != FaceWHDpos[1]) or \
           (self.change_value[2] != FaceWHDpos[2]):
            self.change_time_2 = time.time()
            while (self.change_time_2 - self.change_time_1 <= 0.05):
                self.change_time_2 = time.time()        

        self.change_value[0] = FaceWHDpos[0]
        self.change_value[1] = FaceWHDpos[1]
        self.change_value[2] = FaceWHDpos[2]

        self.position.up_down = FaceWHDpos[0]
        self.position.left_right = FaceWHDpos[1]
        self.position.far_near = FaceWHDpos[2]

        self.pub.publish(self.position)

        return FaceWHDpos


    #ResizedImg = cv2.resize(FaceImg, (int(width/4), int(height/4))) #画像、横、縦　Img.shapeと順番が逆転

    #def Show(self):
    #    height, width, channels = frame.shape[:3] #配列の成分を取得
    #    print("画面の大きさは、高さが" + str(height) + "で、幅が" + str(width) + "です。")


if __name__ == '__main__':

    #ノードの初期化
    rospy.init_node("Camera") #ノードの初期化

    #ビデオキャプチャーオブジェクトを取得
    capture = cv2.VideoCapture(-1) #カメラの設定
    ret, frame = capture.read()

    if ret:
        print("カメラを使うことができます。")
        
        height, width, channels = frame.shape[:3] #配列の成分を取得
        #print("画面の大きさは、高さが" + str(height) + "で、幅が" + str(width) + "です。")

        CMSD = CamFaceDict() #クラスの実体化
   
        #顔検出関数の繰り返しの実行
        while(True):
            ret, frame = capture.read(0)

            FacePos = np.zeros(3)

            FacePos = CMSD.FaceShow("/home/ri-one/catkin_ws/src/carry_food/haarcascade_frontalface_alt.xml", frame)
            #FacePos = CMSD.FaceShow("/home/rione/Rione/catkin_ws/src/spr-16TEST/haarcascade_frontalface_alt.xml", frame)
            print("上下は" + str(FacePos[0]) + "左右は" + str(FacePos[1]) + "遠近は" + str(FacePos[2]))

            cv2.imshow('frame',frame)
   

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        capture.release() 
        cv2.destroyAllWindows() #終了後windowsを閉じる

    else:
        print("カメラを使うことができません。")
    
