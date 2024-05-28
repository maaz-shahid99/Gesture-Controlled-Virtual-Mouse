import cv2
import numpy as np
import mediapipe as mp
import pyautogui

# Define the dimensions of the camera input
wCam, hCam = 640, 480  # Use a lower resolution for faster processing

# Initialize previous palm distance and zoom factor
prev_palm_distance = None
zoom_factor = 2.0
zoom_speed = 5.0  # Adjust zoom speed as needed
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

        # Draw hand landmarks and get palm positions
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on image
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

            hand_landmarks_list = results.multi_hand_landmarks

            if len(hand_landmarks_list) == 2:
                # Get landmarks for each detected hand
                hand1_landmarks = hand_landmarks_list[0]
                hand2_landmarks = hand_landmarks_list[1]

                # Get palm landmark of hand 1 (Center of the hand)
                palm1 = hand1_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                # Get palm landmark of hand 2 (Center of the hand)
                palm2 = hand2_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                # Calculate distance between palm landmarks
                palm_distance = np.sqrt((palm2.x - palm1.x) ** 2 + (palm2.y - palm1.y) ** 2)

                if prev_palm_distance is not None:
                    # Determine zoom action based on palm movement
                    if palm_distance > prev_palm_distance:
                        # Zoom out (increase zoom factor)
                        pyautogui.scroll(20)  # Scroll up (zoom in)
                        zoom_factor -= zoom_speed
                    elif palm_distance < prev_palm_distance:
                        # Zoom in (decrease zoom factor)
                        pyautogui.scroll(-20)  # Scroll down (zoom out)
                        zoom_factor += zoom_speed

                    # Limit zoom factor to reasonable bounds
                    zoom_factor = max(0.1, min(zoom_factor, 3.0))

                # Update previous palm distance
                prev_palm_distance = palm_distance

        # Apply smoothing to the zoom factor for gradual transitions
        zoom_factor = alpha * zoom_factor + (1 - alpha) * zoom_factor

        # Flip image horizontally
        img = cv2.flip(img, 1)
        cv2.imshow("Hand Gesture Zoom", img)

        # Handle closing the window
        if cv2.waitKey(10) == ord('q'):
            break
