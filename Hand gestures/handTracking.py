import cv2
import time
import mediapipe as mp
import math
import numpy as np
from google.protobuf.json_format import MessageToDict


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        
        self.tipIds = [4,8,12,16,20]
        
    
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        
        if self.results.multi_hand_landmarks:
            # Image is not flipped so its reading right as left and left as right
            try:
                # print(MessageToDict(self.results.multi_handedness[0])['classification'][0]['label'])
                if (len(self.results.multi_handedness) == 1 and MessageToDict(self.results.multi_handedness[0])['classification'][0]['label'] == 'Right'):
                    self.results.multi_hand_landmarks.append(self.results.multi_hand_landmarks[0])
                    self.results.multi_hand_landmarks[0] = []
                    
                    # self.results.multi_handedness.append(self.results.multi_handedness[0])
                    # self.results.multi_handedness[0] = []
                    
                    
                elif (MessageToDict(self.results.multi_handedness[0])['classification'][0]['label'] == 'Right'):
                    storage = self.results.multi_hand_landmarks[0]
                    self.results.multi_hand_landmarks[0] = self.results.multi_hand_landmarks[1]
                    self.results.multi_hand_landmarks[1] = storage
                    
                    # storage = self.results.multi_handedness[0]
                    # self.results.multi_handedness[0] = self.results.multi_handedness[1]
                    # self.results.multi_handedness[1] = storage
            except:
                pass
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        
        return img
    
    def findPosition(self, img, handNo = 0, draw=True):
        if (handNo == 0):
            self.lmList1 = []
            try:
                if self.results.multi_hand_landmarks[handNo]:
                    myHand = self.results.multi_hand_landmarks[handNo]
                    for id, lm in enumerate(myHand.landmark):
                            #print(id, lm)
                            h,w,c = img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            #print(id, cx, cy)
                            self.lmList1.append([id, cx, cy])
                            if draw:
                                cv2.circle(img, (cx,cy), 5, (255, 127, 0), cv2.FILLED)
            
                return self.lmList1
            except:
                return self.lmList1
        elif (handNo == 1):
            self.lmList2 = []
            try:
                if self.results.multi_hand_landmarks[handNo]:
                    myHand = self.results.multi_hand_landmarks[handNo]
                    for id, lm in enumerate(myHand.landmark):
                            #print(id, lm)
                            h,w,c = img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            #print(id, cx, cy)
                            self.lmList2.append([id, cx, cy])
                            if draw:
                                cv2.circle(img, (cx,cy), 5, (255, 50, 0), cv2.FILLED)
            
                return self.lmList2
            except:
                return self.lmList2
        else:
            return []
    
    def fingersUp(self, handNo = 0):
        fingers = []
        try:
            if (handNo == 0):
                # Thumb
                if self.lmList1[self.tipIds[0]][1] > self.lmList1[self.tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                    
                for i in range (1,5):
                    if self.lmList1[self.tipIds[i]][2] < self.lmList1[self.tipIds[i] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
            elif (handNo == 1):
                # Thumb
                if self.lmList2[self.tipIds[0]][1] < self.lmList2[self.tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                    
                for i in range (1,5):
                    if self.lmList2[self.tipIds[i]][2] < self.lmList2[self.tipIds[i] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                    
            return fingers
        except:
            return []
        
    def findDistance(self, p1, p2, img, draw=True, r=5, t=3, handNo = 0):
        if (handNo == 0):
            x1, y1 = self.lmList1[p1][1:]
            x2, y2 = self.lmList1[p2][1:]
        elif (handNo == 1):
            x1, y1 = self.lmList2[p1][1:]
            x2, y2 = self.lmList2[p2][1:]
            
        cx, cy = (x1+x2) // 2, (y1+y2) // 2
        
        if draw:
            pass
            cv2.line(img, (x1, y1), (x2, y2), (0,0,255), t)
            cv2.circle(img, (x1,y1), r, (255,0,255), cv2.FILLED)
            cv2.circle(img, (x2,y2), r, (255,0,255), cv2.FILLED)
            cv2.circle(img, (cx,cy), r, (0,0,255), cv2.FILLED)
            
        length = math.hypot(x2-x1, y2-y1)
        
        return length, img, [x1,y1, x2,y2, cx,cy]
        
    
    


def main():
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    pTime = 0
    cTime = 0
    
    
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime
        
        cv2.putText(img, str(int(fps)), (5,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 2)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) == 13:
            break
        
        
    cap.release()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    main()
    


