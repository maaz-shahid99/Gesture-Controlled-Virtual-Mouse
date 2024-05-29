import cv2
import mediapipe as mp
import pyautogui
import time

class HandGestureController:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=max_num_hands,
                                         min_detection_confidence=min_detection_confidence,
                                         min_tracking_confidence=min_tracking_confidence)
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.screen_width, self.screen_height = pyautogui.size()
        self.finger_tips = [8, 12, 16, 20]
        self.panning = False

    def is_closed_fist(self, lm_list):
        return all(lm_list[tip].y > lm_list[tip - 2].y for tip in self.finger_tips)

    def is_victory_gesture(self, lm_list):
        index_tip = lm_list[8]
        middle_tip = lm_list[12]
        return (index_tip.y < lm_list[6].y and middle_tip.y < lm_list[10].y)

    def process_hand_gestures(self, hand_landmarks):
        lm_list = [lm for lm in hand_landmarks.landmark]
        hand_center_x = int(lm_list[9].x * self.screen_width)
        hand_center_y = int(lm_list[9].y * self.screen_height)

        if self.is_closed_fist(lm_list):
            if not self.panning:
                pyautogui.mouseDown(button='middle')
                self.panning = True
            pyautogui.moveTo(hand_center_x, hand_center_y, duration=0.1)
        elif self.is_victory_gesture(lm_list):
            if self.panning:
                pyautogui.mouseUp(button='middle')
                self.panning = False

    def run(self):
        while True:
            ret, img = self.cap.read()
            if not ret:
                break

            img = cv2.flip(img, 1)
            results = self.hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.process_hand_gestures(hand_landmarks)
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            cv2.imshow("Hand Gesture Recognition", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.05)  # Introduce a small delay to prevent overwhelming the system

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = HandGestureController()
    controller.run()
