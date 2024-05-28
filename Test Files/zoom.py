import cv2
import numpy as np
import mediapipe as mp
import pyautogui

# Define the dimensions of the camera input
wCam, hCam = 640, 480  # Use a lower resolution for faster processing

# Initialize previous finger distances and zoom factor
prev_finger_distance = None
zoom_factor = 1.0
zoom_speed = 0.5  # Adjust zoom speed as needed
alpha = 0.1  # Smoothing factor for zoom factor (0 < alpha < 1)

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
    while True:
        # Read from camera
        _, img = cap.read()
        if not _:
            continue



        # Convert BGR image to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect hand landmarks
        results = hands.process(img_rgb)

        # Draw hand landmarks and get finger tip positions
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on image
                 mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                                  )

            hand_landmarks_list = results.multi_hand_landmarks

            if len(hand_landmarks_list) == 2:
                # Get landmarks for each detected hand
                hand1_landmarks = hand_landmarks_list[0]
                hand2_landmarks = hand_landmarks_list[1]

                # Get coordinates of thumb tip and index finger tip from hand 1
                thumb1_tip = hand1_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index1_tip = hand1_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Get coordinates of thumb tip and index finger tip from hand 2
                thumb2_tip = hand2_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index2_tip = hand2_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Calculate distances between thumb and index finger pairs
                distance1 = np.sqrt((index1_tip.x - thumb1_tip.x) ** 2 + (index1_tip.y - thumb1_tip.y) ** 2)
                distance2 = np.sqrt((index2_tip.x - thumb2_tip.x) ** 2 + (index2_tip.y - thumb2_tip.y) ** 2)

                # Calculate average finger distance
                avg_finger_distance = (distance1 + distance2) / 2

                if prev_finger_distance is not None:
                    # Determine zoom action based on finger movement
                    if avg_finger_distance > prev_finger_distance:
                        # Zoom out (increase zoom factor)
                        pyautogui.scroll(10)  # Scroll up (zoom in)
                        zoom_factor -= zoom_speed
                    elif avg_finger_distance < prev_finger_distance:
                        # Zoom in (decrease zoom factor)
                        pyautogui.scroll(-10)  # Scroll up (zoom in)
                        zoom_factor += zoom_speed

                    # Limit zoom factor to reasonable bounds
                    zoom_factor = max(0.1, min(zoom_factor, 3.0))

                # Update previous finger distance
                prev_finger_distance = avg_finger_distance

        # Apply smoothing to the zoom factor for gradual transitions
        zoom_factor = alpha * zoom_factor + (1 - alpha) * zoom_factor
        # Flip image horizontally
        img = cv2.flip(img, 1)
        cv2.imshow("Hand Gesture Zoom",img)

        # Handle closing the window
        if cv2.waitKey(10) == ord('q'):
            break