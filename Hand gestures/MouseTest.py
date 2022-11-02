import cv2
import time
import numpy as np
import handTrackingTest as htm
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


# Camera
cap = cv2.VideoCapture(0)
widthCam, heightCam = 1280, 720 
cap.set(3, widthCam) # Width
cap.set(4, heightCam) # Height


# Hands and detection
detector = htm.handDetector(maxHands=2)
pTime, cTime = 0, 0
previousX, previousY = 0,0
currentX, currentY = 0,0
smoothening = 6
widthScreen, heightScreen = pyautogui.size()
#print(widthScreen, heightScreen)


# Dragging
drag = 0
dragX = 0
dragY = 0

# Volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0



while True:
    #Find hand landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList1 = detector.findPosition(img, handNo = 0)
    # Check which fingers 1 are up
    fingers1 = detector.fingersUp(handNo = 0)
    #print(fingers1)
    
    # If there are hands in the screen
    if len(lmList1) != 0:
        indexX, indexY = lmList1[8][1:]
        
        # Convert Coordinates (Camera => Screen)
        indexX = np.interp(indexX, (100,widthCam - 100), (0,widthScreen)) # moving your index finger across the camera will interpret that as moving across the computer screen
        indexY = np.interp(indexY, (100,heightCam - 400), (0,heightScreen))
        
        # Smoothen Values
        currentX = previousX + (indexX - previousX)/smoothening
        currentY = previousY + (indexY - previousY)/smoothening
        
        # Find landmarks and which fingers 2 is up
        lmList2 = detector.findPosition(img, handNo = 1)
        fingers2 = detector.fingersUp(handNo = 1)
        
        if (len(lmList2) != 0):    
            if (fingers2[0] == 0 and fingers2[1] == 1 and fingers2[2] == 0 and fingers2[3] == 0 and fingers2[4] == 0):
                length, img, lineInfo = detector.findDistance(4, 8, img)
                #print (length)
                
                # Hand (20, 200) / Vol (-65.25, 0)
                vol = int(np.interp(length, [30,250], [minVol,maxVol]))
                volBar = int(np.interp(length, [30,250], [400,150]))
                volPer = int(np.interp(length, [30,250], [0,100]))
                volume.SetMasterVolumeLevel(vol, None)
                
                if vol == -65:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 5, (0,255,0), cv2.FILLED)
        
        
        ### Mouse ###
        elif (fingers1[2] == 0 and fingers1[3] == 0 and fingers1[4] == 0):
            
            
            # Only index is up (moving mode)
            if (fingers1[0] == 1 and fingers1[1] == 1):
                
                # Move Mouse
                pyautogui.moveTo(widthScreen - currentX, currentY)
                previousX,previousY = currentX, currentY
            
            ## Maximize Window ##
             # Find distance between thumb and palm 
            length, img, lineInfo = detector.findDistance(4, 8, img)
            #print(length)
            if (length > 380 and length < 450):
                pyautogui.hotkey('win', 'up')
                
            ## Minimize Window ##
            if (fingers1[0] == 1 and fingers1[1] == 0):
                pyautogui.hotkey('win', 'down')
        
            
            ## Click ##
            # Find distance between thumb and palm 
            length, img, lineInfo = detector.findDistance(4, 5, img, draw=False)
            #print(length) 
            if length < 50: # 100
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 5, (0,255,0), cv2.FILLED)
                pyautogui.click()
                
            
                


        # Drag mode
        elif (fingers1[1] == 1 and fingers1[2] == 1 and fingers1[3] == 0 and fingers1[4] == 0):
            
            # Find distance between thumb and palm 
            length, img, lineInfo = detector.findDistance(4, 5, img)
            #print(length)
            
            # Only index is up (moving mode)
            if (fingers1[0] == 1 and fingers1[1] == 1 and fingers1[2] == 1):
                
                # Move Mouse
                pyautogui.moveTo(widthScreen - currentX, currentY)
                previousX,previousY = currentX, currentY
                
            if (fingers1[0] == 0):
                if (drag == 0):
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 5, (0,255,0), cv2.FILLED)
                    dragX = widthScreen - currentX
                    dragY = currentY
                    drag = 1
                    time.sleep(0.25)
                elif (drag == 1):
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 5, (0,255,0), cv2.FILLED)
                    pyautogui.moveTo(dragX, dragY, duration=0.25)
                    # pyautogui.click()
                    pyautogui.dragTo(widthScreen - currentX, currentY, duration=0.5)
                    drag = 0
                    
        
                    
    

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    img = cv2.flip(img, 1)
    if (drag == 0):
        cv2.putText(img, "Drag: Off", (5,700), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 1)
    else:
        cv2.putText(img, "Drag: On", (5,700), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 1)
    if (volPer == 0):
        pass
        #cv2.putText(img, f'Volume: {volPer}%', (5, 660), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 1)
    else:
        cv2.putText(img, f'Volume: {volPer}%', (5, 660), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 1)
    cv2.putText(img, str(int(fps)), (5,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 13:
        break
    
    
cap.release()
cv2.destroyAllWindows()