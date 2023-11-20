import cv2
import numpy as np
import time
import HandTracking as ht
import autopy  

pTime = 0   
#height and width of webcamera           
width = 640          
height = 480   
#frame reduction      
frameR = 100  
# it is used for slower and faster movement for mouse         
smoothening = 6  
#previous cordinates of x,y     
prev_x, prev_y = 0, 0 
#current cordinates of x,y  
curr_x, curr_y = 0, 0

cap = cv2.VideoCapture(0)  
cap.set(3, width)      
cap.set(4, height)

detector = ht.handDetector(maxHands=1) 
#it will give the size of the screen               
screen_width, screen_height = autopy.screen.size()    
while True:
    #11. to display

    #1.finding the hand landmarks
    success, img = cap.read()
    img = detector.findHands(img)                  
    lmlist, bbox = detector.findPosition(img)        

    #2. get the tip of the index and middle fingers
    if len(lmlist)!=0:
        #for first finger index cordinates
        x1, y1 = lmlist[8][1:]
        #for middle figer index cordinates
        x2, y2 = lmlist[12][1:]

        #3. checking which finger is up
        fingers = detector.fingersUp() 
        #making a region for while we are at distance from screen then the weecame can detect our hand
        cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255), 2) 
       #4. only index finger:moving mode
        if fingers[1] == 1 and fingers[2] == 0:   
            #5. convert cordinates for x3:width ,y3: height
            x3 = np.interp(x1, (frameR,width-frameR), (0,screen_width))
            y3 = np.interp(y1, (frameR, height-frameR), (0, screen_height))

            #6. smoothen values
            #we are diluting the values instead of directing sending the values
            # if we multiply the smoothing then values goes into the points
            curr_x = prev_x + (x3 - prev_x)/smoothening
            curr_y = prev_y + (y3 - prev_y) / smoothening
            print(curr_x,curr_y)
             
            #7. move mouse easily
            #7.1 fliping the cordinates using:screen_width - curr_x
            autopy.mouse.move(screen_width - curr_x, curr_y)
            #making circle with radius 7 on a tip finger ,when we are in moving mode 
            cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
            
            #updating the previous values by current
            prev_x, prev_y = curr_x, curr_y

            #8. check if both fingers are up then clicking mode is performed
        if fingers[1] == 1 and fingers[2] == 1:
             #9. find the distance between fingers ,if distance is short then we perform click
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 40:
                #4 and 5 is because we use use in finddistance function cur_x, cur_y is at index 4 and 5
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
        if fingers[0] == 1 and fingers[1] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if(length < 40):
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)


          #11. frame rate      
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    k = cv2.waitKey(10)
    if k == 27:
        break