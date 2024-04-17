import cv2
import time
import numpy as np
import mediapipe as mp
import pyautogui
import win32api

# Define the dimensions of the camera input and the region of interest (ROI)
wCam, hCam = 640, 480
screen_width, screen_height = pyautogui.size()
pTime = 0

cap = cv2.VideoCapture(1)

cap.set(3, wCam)
cap.set(4, hCam)


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
detector = mp_hands.Hands(max_num_hands=1,
                      min_detection_confidence=0.7, 
                      min_tracking_confidence=0.5)

index_y = 0
knuckle_y = 0
mid_fing_y = 0
index_x = 0
mid_fing_x = 0
left_click_flag = False
right_click_flag = False

# Define smoothing factor (0 < alpha < 1)
alpha = 0.75

# Initialize previous cursor position
prev_cursor_x = None
prev_cursor_y = None

while True:


    #1. Find hand Landmarkrs
    _, img = cap.read()

    #BGR to RGB conversion
    # RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    #Detections
    result = detector.process(img)

    RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    hand_landmarks = None  # Initialize hand_landmarks outside the loop
    
    if result.multi_hand_landmarks:
        # Access the first hand_landmarks directly without looping
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS, 
                                  mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                                  )

    #2. Get the tip of Index and Middle Fingers        
    
    if hand_landmarks:
        for id, landmark in enumerate(hand_landmarks.landmark): 
            # print(landmark.x, landmark.y)
            x = int(landmark.x *wCam)
            y = int(landmark.y *hCam)
            # print(x,y)

            if id == 3: #Thumb Knuckle
                cv2.circle(img=img, center=(x,y), radius=20, color=(0,255,255))
                
                knuckle_x = screen_width - (x * screen_width / wCam)
                knuckle_y = screen_height/hCam*y

                if 0 < knuckle_x < screen_width and 0 < knuckle_y < screen_height:
                    if prev_cursor_x is None or prev_cursor_y is None:
                        smoothed_x = knuckle_x
                        smoothed_y = knuckle_y
                    else:
                        smoothed_x = alpha * knuckle_x + (1 - alpha) * prev_cursor_x
                        smoothed_y = alpha * knuckle_y + (1 - alpha) * prev_cursor_y

                    # Move cursor to the smoothed position
                    
                    win32api.SetCursorPos((int(smoothed_x),int(smoothed_y)))
                    print(int(smoothed_x),int(smoothed_y),x,y)

                    # Update previous cursor position
                    prev_cursor_x = smoothed_x
                    prev_cursor_y = smoothed_y

                    if abs(knuckle_y - index_y) < 50 and not left_click_flag:
                        print('left click')
                        pyautogui.click()
                        left_click_flag = True
                        right_click_flag = False

                    elif abs(knuckle_y - mid_fing_y) < 50 and not right_click_flag:
                        print('right click')
                        pyautogui.click(button='right')
                        right_click_flag = True
                        left_click_flag = False
                
                    else:
                        left_click_flag = False
                        right_click_flag = False

            if id == 8: #Index Finger
                cv2.circle(img=img, center=(x,y), radius=20, color=(0,255,255))
                index_x = (screen_width - (x * screen_width / wCam))
                index_y = (screen_height/hCam*y)
                

            if id == 12: #Middle Finger
                cv2.circle(img=img, center=(x,y), radius=20, color=(0,255,255))
                mid_fing_x = screen_width - (x * screen_width / wCam)
                mid_fing_y = screen_height/hCam*y
                
                # Add a threshold for double-click detection
                if abs(index_x - mid_fing_x) < 30 and not right_click_flag and not left_click_flag:
                    print('double click')
                    pyautogui.doubleClick()
                    right_click_flag = True
                    left_click_flag = False

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
