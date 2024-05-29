import cv2
import numpy as np
import mediapipe as mp
import pyautogui

class HandGestureZoom:
    def __init__(self, cam_index=0, wCam=640, hCam=480):
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(3, wCam)
        self.cap.set(4, hCam)
        self.prev_finger_distance = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def process_frame(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        return results

    def detect_gesture_and_zoom(self, results, img):
        if results.multi_hand_landmarks:
            hand_landmarks_list = results.multi_hand_landmarks

            if len(hand_landmarks_list) == 2:
                hand1_landmarks = hand_landmarks_list[0]
                hand2_landmarks = hand_landmarks_list[1]

                thumb1_tip = hand1_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                index1_tip = hand1_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb2_tip = hand2_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                index2_tip = hand2_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                distance1 = self.calculate_distance(index1_tip, thumb1_tip)
                distance2 = self.calculate_distance(index2_tip, thumb2_tip)
                avg_finger_distance = (distance1 + distance2) / 2

                if self.prev_finger_distance is not None:
                    if avg_finger_distance > self.prev_finger_distance:
                        pyautogui.scroll(-10)  # Scroll down (zoom out)
                    elif avg_finger_distance < self.prev_finger_distance:
                        pyautogui.scroll(10)  # Scroll up (zoom in)

                self.prev_finger_distance = avg_finger_distance

            for hand_landmarks in hand_landmarks_list:
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return img

    def run(self):
        while True:
            ret, img = self.cap.read()
            if not ret:
                break

            img = cv2.flip(img, 1)
            results = self.process_frame(img)
            img = self.detect_gesture_and_zoom(results, img)

            cv2.imshow("Hand Gesture Zoom", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    hand_gesture_zoom = HandGestureZoom()
    hand_gesture_zoom.run()
