import cv2
import mediapipe as mp
import numpy as np
from joblib import load
from sklearn.preprocessing import Normalizer
from pynput.keyboard import Key, Controller as KeyboardController
import time

## Open capture with video path
capture = cv2.VideoCapture(0)

## Initialize mediapipe hand detection function
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

## Load trained model and initialize a normalizer
model = load("model.joblib")
normalizer = Normalizer()

## Create a keyboard controller
keyboard = KeyboardController()

## Define variables for output video
outputVid = None  # Placeholder for VideoWriter

## Helper function to create a bounding box around each hand.
## Takes in video frame img and hand landmarks lm
def createBoundingBox(img, lm):

    ## Initialize empty array to store all landmarks of
    ## hand landmark lm
    lm_array = np.empty((0,2), int)

    ## For each landmark in hand landmark, append
    ## minimum points to array
    for _, landmark in enumerate(lm.landmark):

        width, height = img.shape[1], img.shape[0]
        ## Calculate minimum point between landmark
        ## position and size of video frame
        lm_x = min(int(landmark.x * width), width - 1)
        lm_y = min(int(landmark.y * height), height - 1)

        ## Create a point using the minimum for landmark
        lm_point = [np.array((lm_x, lm_y))]

        ## Append point to array
        lm_array = np.append(lm_array, lm_point, axis=0)

    ## Using built-in method boundingRect, get the x,y,w,h
    ## from the bounding box of lm_array
    x, y, w, h = cv2.boundingRect(lm_array)

    ## Define positions for bouding box to encapsulate hand
    x_min = x - 20
    y_min = y - 15
    x_max = x + w + 20
    y_max = y + h + 15

    return [x_min, y_min, x_max, y_max]

## Helper function to calculate twist gesture
def detect_twist(handLms):
    # Assuming handLms is a single hand landmark object
    # Check the relative positions of landmarks to detect twist
    # For example, you can compare the positions of thumb and index finger landmarks

    # Example logic:
    # Calculate the angle between thumb and index finger landmarks
    thumb_x = handLms.landmark[mpHands.HandLandmark.THUMB_TIP].x
    thumb_y = handLms.landmark[mpHands.HandLandmark.THUMB_TIP].y
    index_x = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x
    index_y = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y

    # Calculate angle or use a simpler condition based on relative positions
    # For example, if thumb is to the left of index finger, it's a twist left gesture
    if thumb_x < index_x:
        return 'left'
    elif thumb_x > index_x:
        return 'right'
    else:
        return None

## Define variables for output video
h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
size = (w, h)

## Create VideoWriter instance with variables taken from input
outputVid = cv2.VideoWriter("result.avi", cv2.VideoWriter_fourcc('M','J','P','G'), 24, size, isColor=True)

## While capture is open
while(capture.isOpened()):

    ## Read the frame from capture
    read, frame = capture.read()

    frame = cv2.flip(frame, 1)

    ## If frame was properly read
    if read == True:

        ## Convert frame to RGB for proper mediapipe detection
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ## Process each frame to get hand landmarks
        results = hands.process(rgbFrame)

        ## If results exist
        if results.multi_hand_landmarks:

            ## For each hand detected
            for handLms in results.multi_hand_landmarks:

                ## Call upon createBoundingBox() method to get bounding box coordinates
                boundingBox = createBoundingBox(frame, handLms)

                ## Draw a rectangle around each processed bounding box
                cv2.rectangle(frame, (boundingBox[0], boundingBox[1]), (boundingBox[2], boundingBox[3]), (0, 255, 0), 2)

                ## Draw the connections between landmarks for better visualization
                mp_drawing.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

                ## Detect twist gesture
                twist_direction = detect_twist(handLms)

                ## Perform action based on twist gesture
                if twist_direction == 'right':
                    # Perform right rotation action
                    keyboard.press(Key.alt)
                    keyboard.press(Key.right)
                    time.sleep(0.1)
                    keyboard.release(Key.right)
                    keyboard.release(Key.alt)
                    action_text = "Right Rotation"
                elif twist_direction == 'left':
                    # Perform left rotation action
                    keyboard.press(Key.alt)
                    keyboard.press(Key.left)
                    time.sleep(0.1)
                    keyboard.release(Key.left)
                    keyboard.release(Key.alt)
                    action_text = "Left Rotation"

    cv2.imshow("Frame", frame)

    ## Write frame with detection results to VideoWriter instance outputVid
    outputVid.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

## Release video capture and writer, and close all windows
capture.release()
outputVid.release()
cv2.destroyAllWindows()
