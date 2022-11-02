import cv2
import time
import numpy as np
import handTracking as htm
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL




widthCam, heightCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, widthCam) # Width
cap.set(4, heightCam) # Height
pTime = 0
cTime = 0

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
print(volRange)




while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        length, img, lineInfo = detector.findDistance(4, 8, img)
        #print (length)
        
        # Hand (20, 200) / Vol (-65.25, 0)
        vol = int(np.interp(length, [30,350], [minVol,maxVol])) # -57, 
        volBar = int(np.interp(length, [30,350], [400,150]))
        volPer = int(np.interp(length, [30,350], [0,100]))
        print(vol)
        volume.SetMasterVolumeLevel(-5, None)

        
        if vol == -65:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 5, (0,255,0), cv2.FILLED)
            
        
        cv2.rectangle(img, (50,150), (85,400), (255, 0,0), 3)
        cv2.rectangle(img, (50, volBar), (85,400), (255, 0,0), cv2.FILLED)
        cv2.putText(img, f'{volPer} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0,0), 3)
            
        
        
        
        


    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    cv2.putText(img, str(int(fps)), (5,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 13:
        break
    
    
cap.release()
cv2.destroyAllWindows()