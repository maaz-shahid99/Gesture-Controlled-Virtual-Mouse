import cv2
import mediapipe as mp
import pyautogui

class HandGestureController:
    def __init__(self, cam_index=0, wCam=640, hCam=480, cursor_res=(240, 180), alpha=0.2):
        self.wCam, self.hCam = wCam, hCam
        self.screen_width, self.screen_height = pyautogui.size()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.cursor_res_x, self.cursor_res_y = cursor_res
        self.alpha = alpha
        self.input_range_x = (int((self.wCam - self.cursor_res_x) / 2), int(self.cursor_res_x + (self.wCam - self.cursor_res_x) / 2))
        self.input_range_y = (int((self.hCam - self.cursor_res_y) / 2), int(self.cursor_res_y + (self.hCam - self.cursor_res_y) / 2))
        self.pLoc_X, self.pLoc_Y = 0, 0
        self.shift_held = False  # Track the shift key state

    def is_open_palm(self, lm_list):
        finger_tips = [8, 12, 16, 20]
        return all(lm_list[tip].y < lm_list[tip - 2].y for tip in finger_tips)

    def is_victory_gesture(self, lm_list):
        return (lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y)

    def is_closed_fist(self, lm_list):
        finger_tips = [8, 12, 16, 20]
        return all(lm_list[tip].y > lm_list[tip - 2].y for tip in finger_tips)

    def map_value(self, value, input_range, output_range):
        input_min, input_max = input_range
        output_min, output_max = output_range
        mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
        return int(max(min(mapped_value, output_max), output_min))

    def process_frame(self, img):
        img = cv2.flip(img, 1)
        h, w, c = img.shape
        results = self.hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        gesture_label_right = ""
        gesture_label_left = ""
        right_hand_detected = False
        left_hand_detected = False

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

                    if right_hand_detected:
                        x = int(lm_list[8].x * self.wCam)
                        y = int(lm_list[8].y * self.hCam)
                        cLoc_X = int(self.screen_width / self.wCam * x)
                        cLoc_Y = int(self.screen_height / self.hCam * y)
                        self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

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

                    if left_hand_detected:
                        self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                if right_hand_detected and left_hand_detected:
                    # Check for specific gesture combination
                    if gesture_label_left == "Closed Fist" and gesture_label_right == "Open Palm":
                        pyautogui.dragTo(cLoc_X, cLoc_Y, button='middle')
                        if not self.shift_held:
                            pyautogui.keyDown('shift')
                            self.shift_held = True

        if not (right_hand_detected and left_hand_detected) and self.shift_held:
            pyautogui.keyUp('shift')
            self.shift_held = False

        return img

    def run(self):
        while True:
            ret, img = self.cap.read()
            if not ret:
                print("No frame received. Exiting.")
                break

            img = self.process_frame(img)
            cv2.imshow("Hand Gesture Recognition", img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        if self.shift_held:
            pyautogui.keyUp('shift')

if __name__ == "__main__":
    gesture_controller = HandGestureController()
    gesture_controller.run()
