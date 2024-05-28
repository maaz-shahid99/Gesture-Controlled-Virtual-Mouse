# grab and rotate and zoom in zoom out merged

import cv2
import numpy as np
import mediapipe as mp
import pyautogui

class HandGestureController:
    def __init__(self, cam_index=0, wCam=640, hCam=480):
        self.wCam, self.hCam = wCam, hCam
        self.screen_width, self.screen_height = pyautogui.size()
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_finger_distance = None
        self.shift_held = False

    def is_open_palm(self, lm_list):
        finger_tips = [8, 12, 16, 20]
        return all(lm_list[tip].y < lm_list[tip - 2].y for tip in finger_tips)

    def is_victory_gesture(self, lm_list):
        return (lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y)

    def is_closed_fist(self, lm_list):
        finger_tips = [8, 12, 16, 20]
        return all(lm_list[tip].y > lm_list[tip - 2].y for tip in finger_tips)

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def process_frame(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        return results

    def detect_gesture_and_perform_action(self, results, img):
        right_hand_detected = False
        left_hand_detected = False
        gesture_label_right = ""
        gesture_label_left = ""

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                lm_list = [lm for lm in hand_landmarks.landmark]

                if handedness.classification[0].label == 'Right':
                    if self.is_open_palm(lm_list):
                        gesture_label_right = "Open Palm"
                        right_hand_detected = True
                    elif self.is_victory_gesture(lm_list):
                        gesture_label_right = "Victory"
                        right_hand_detected = True
                    elif self.is_closed_fist(lm_list):
                        gesture_label_right = "Closed Fist"
                        right_hand_detected = True

                elif handedness.classification[0].label == 'Left':
                    if self.is_open_palm(lm_list):
                        gesture_label_left = "Open Palm"
                        left_hand_detected = True
                    elif self.is_victory_gesture(lm_list):
                        gesture_label_left = "Victory"
                        left_hand_detected = True
                    elif self.is_closed_fist(lm_list):
                        gesture_label_left = "Closed Fist"
                        left_hand_detected = True

                if right_hand_detected and left_hand_detected:
                    if gesture_label_left == "Closed Fist" and gesture_label_right == "Open Palm":
                        pyautogui.dragTo(int(lm_list[8].x * self.screen_width), int(lm_list[8].y * self.screen_height), button='middle')
                        if not self.shift_held:
                            pyautogui.keyDown('shift')
                            self.shift_held = True

                if not (right_hand_detected and left_hand_detected) and self.shift_held:
                    pyautogui.keyUp('shift')
                    self.shift_held = False

            if len(results.multi_hand_landmarks) == 2:
                hand1_landmarks = results.multi_hand_landmarks[0]
                hand2_landmarks = results.multi_hand_landmarks[1]

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

            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return img

    def run(self):
        while True:
            ret, img = self.cap.read()
            if not ret:
                break

            img = cv2.flip(img, 1)
            results = self.process_frame(img)
            img = self.detect_gesture_and_perform_action(results, img)

            cv2.imshow("Hand Gesture Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        if self.shift_held:
            pyautogui.keyUp('shift')

if __name__ == "__main__":
    hand_gesture_controller = HandGestureController()
    hand_gesture_controller.run()
