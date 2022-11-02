import cv2
import time
import handTracking as htm

cap = cv2.VideoCapture(0)
detector = htm.handDetector()
pTime = 0
cTime = 0


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        length, img, lineInfo = detector.findDistance(8, 12, img)
        print(length)
        fingers = detector.fingersUp()
        #print(fingers)
        #print(lmList[4])

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    cv2.putText(img, str(int(fps)), (5,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,5,5), 2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == 13:
        break
    
    
cap.release()
cv2.destroyAllWindows()