import cv2
import time
import mediapipe as mp
import pyautogui
import win32api

# Define the dimensions of the camera input and the region of interest (ROI)
wCam, hCam = 640, 480
screen_width, screen_height = pyautogui.size()
pTime = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
#detector = mp_hands.Hands()
detector = mp_hands.Hands(max_num_hands=1,
                      min_detection_confidence=0.7,
                      min_tracking_confidence=0.5)

index_y = 0
index_x = 0
knuckle_y = 0
mid_fing_y = 0
mid_fing_x = 0

left_click_flag = False
right_click_flag = False

cursor_res_x=240
cursor_res_y=180

input_range_x = (int((wCam-cursor_res_x)/2), int(cursor_res_x+(wCam-cursor_res_x)/2))
input_range_y = (int((hCam-cursor_res_y)/2), int(cursor_res_y+(hCam-cursor_res_y)/2))

# print(input_range_x, input_range_y)

# Define smoothing factor (0 < alpha < 1)
alpha = 5

# Initialize cursor position
pLoc_X, pLoc_Y = 0, 0
cLoc_X, cLoc_Y = 0, 0

def map_value_x(value):
    input_min, input_max = input_range_x
    output_min, output_max = (0,640)

    # Map the input value to the output range
    mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))

    # Make sure the mapped value stays within the output range
    mapped_value = max(min(mapped_value, output_max), output_min)

    return int(mapped_value)

def map_value_y(value):
    input_min, input_max = input_range_y
    output_min, output_max = (0,480)

    # Map the input value to the output range
    mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))

    # Make sure the mapped value stays within the output range
    mapped_value = max(min(mapped_value, output_max), output_min)

    return int(mapped_value)


while True:


    #1. Find hand Landmarkrs
    _, img = cap.read()

    #BGR to RGB conversion
    RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #Detections
    result = detector.process(RGB_frame)

    # RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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

                x = map_value_x(x)
                y = map_value_y(y)

                knuckle_x = screen_width - (x * screen_width / wCam)
                knuckle_y = screen_height/hCam*y


                if 0 < knuckle_x < screen_width and 0 < knuckle_y < screen_height:
                    
                    # Smoothening Cursor Movement
                    cLoc_X = pLoc_X + (knuckle_x - pLoc_X) / alpha
                    cLoc_Y = pLoc_Y + (knuckle_y - pLoc_Y) / alpha

                    #Moving Cursor
                    win32api.SetCursorPos((int(cLoc_X),int(cLoc_Y)))
                    
                    #Updating Cursor Movement
                    pLoc_X, pLoc_Y = cLoc_X, cLoc_Y

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
                if abs(index_x - mid_fing_x) < 20 and not right_click_flag and not left_click_flag:
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
