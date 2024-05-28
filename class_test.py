import cv2
import time
import mediapipe as mp
import pyautogui
import win32api

class HandGestureController:
    def __init__(self, cam_index=0, wCam=640, hCam=480):
        self.wCam, self.hCam = wCam, hCam
        self.screen_width, self.screen_height = pyautogui.size()
        self.pTime = 0

        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.detector = self.mp_hands.Hands(max_num_hands=1,
                                            min_detection_confidence=0.7,
                                            min_tracking_confidence=0.5)

        self.index_y = 0
        self.index_x = 0
        self.knuckle_y = 0
        self.mid_fing_y = 0
        self.mid_fing_x = 0

        self.left_click_flag = False
        self.right_click_flag = False

        self.cursor_res_x = 240
        self.cursor_res_y = 180

        self.input_range_x = (int((self.wCam - self.cursor_res_x) / 2), int(self.cursor_res_x + (self.wCam - self.cursor_res_x) / 2))
        self.input_range_y = (int((self.hCam - self.cursor_res_y) / 2), int(self.cursor_res_y + (self.hCam - self.cursor_res_y) / 2))

        self.alpha = 0.5

        self.prev_cursor_x = None
        self.prev_cursor_y = None

    def map_value(self, value, input_range, output_range):
        input_min, input_max = input_range
        output_min, output_max = output_range

        mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
        return int(max(min(mapped_value, output_max), output_min))

    def process_frame(self):
        _, img = self.cap.read()
        RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.detector.process(RGB_frame)
        hand_landmarks = None

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                                           self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                           self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

        if hand_landmarks:
            self.detect_gestures(img, hand_landmarks)

        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime

        img = cv2.flip(img, 1)
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.imshow("Hand Gesture Control", img)

    def detect_gestures(self, img, hand_landmarks):
        for id, landmark in enumerate(hand_landmarks.landmark):
            x = int(landmark.x * self.wCam)
            y = int(landmark.y * self.hCam)

            if id == 3:
                cv2.circle(img, (x, y), 20, (0, 255, 255), -1)
                knuckle_x = self.map_value(x, self.input_range_x, (0, self.screen_width))
                knuckle_y = self.map_value(y, self.input_range_y, (0, self.screen_height))
                self.move_cursor(knuckle_x, knuckle_y)

                if abs(knuckle_y - self.index_y) < 50 and not self.left_click_flag:
                    print('left click')
                    pyautogui.click()
                    self.left_click_flag = True
                    self.right_click_flag = False

                elif abs(knuckle_y - self.mid_fing_y) < 50 and not self.right_click_flag:
                    print('right click')
                    pyautogui.click(button='right')
                    self.right_click_flag = True
                    self.left_click_flag = False
                else:
                    self.left_click_flag = False
                    self.right_click_flag = False

            if id == 8:
                cv2.circle(img, (x, y), 20, (0, 255, 255), -1)
                self.index_x = self.map_value(x, self.input_range_x, (0, self.screen_width))
                self.index_y = self.map_value(y, self.input_range_y, (0, self.screen_height))

            if id == 12:
                cv2.circle(img, (x, y), 20, (0, 255, 255), -1)
                self.mid_fing_x = self.map_value(x, self.input_range_x, (0, self.screen_width))
                self.mid_fing_y = self.map_value(y, self.input_range_y, (0, self.screen_height))

                if abs(self.index_x - self.mid_fing_x) < 20 and not self.right_click_flag and not self.left_click_flag:
                    print('double click')
                    pyautogui.doubleClick()
                    self.right_click_flag = True
                    self.left_click_flag = False

    def move_cursor(self, x, y):
        if 0 < x < self.screen_width and 0 < y < self.screen_height:
            if self.prev_cursor_x is None or self.prev_cursor_y is None:
                smoothed_x = x
                smoothed_y = y
            else:
                smoothed_x = self.alpha * x + (1 - self.alpha) * self.prev_cursor_x
                smoothed_y = self.alpha * y + (1 - self.alpha) * self.prev_cursor_y

            win32api.SetCursorPos((int(smoothed_x), int(smoothed_y)))
            self.prev_cursor_x = smoothed_x
            self.prev_cursor_y = smoothed_y

    def run(self):
        while True:
            self.process_frame()
            if cv2.waitKey(10) == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    hand_gesture_controller = HandGestureController()
    hand_gesture_controller.run()
