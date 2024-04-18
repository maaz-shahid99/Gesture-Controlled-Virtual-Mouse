import cv2
import time
import numpy as np
import mediapipe as mp

# Define the dimensions of the camera input and the region of interest (ROI)
wCam, hCam = 640, 480
pTime = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
#detector = mp_hands.Hands()
detector = mp_hands.Hands(max_num_hands=2,
                      min_detection_confidence=0.7, 
                      min_tracking_confidence=0.5)

while True:


    #1. Find hand Landmarkrs
    _, img = cap.read()
    
    RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    #Detections
    result = detector.process(img)

    

    hand_landmarks = None  # Initialize hand_landmarks outside the loop
    
    if result.multi_hand_landmarks:
        # Access the first hand_landmarks directly without looping
        for hand_landmarks in result.multi_hand_landmarks:
          mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                                    )



    #11. Frame Rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    #Flip Image
    img = cv2.flip(img, 1)
    cv2.putText(img, str(int(fps)), (20,50),cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)

    #12. Display

    
    cv2.imshow("Imshow", img)

    if cv2.waitKey(10) == ord('q'):
        break