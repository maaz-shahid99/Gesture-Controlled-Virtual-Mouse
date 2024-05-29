import cv2
import time
import mediapipe as mp
import pyautogui
import win32api

class HandTrackingMouseControl:
    def __init__(self):
        self.wCam, self.hCam = 640, 480
        self.screen_width, self.screen_height = pyautogui.size()
        self.pTime = 0

        # self.cap = cv2.VideoCapture(1)
        # self.cap.set(3, self.wCam)
        # self.cap.set(4, self.hCam)

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

        self.input_range_x = (int((self.wCam - self.cursor_res_x) / 2),
                              int(self.cursor_res_x + (self.wCam - self.cursor_res_x) / 2))
        self.input_range_y = (int((self.hCam - self.cursor_res_y) / 2),
                              int(self.cursor_res_y + (self.hCam - self.cursor_res_y) / 2))

        self.alpha = 0.5
        self.prev_cursor_x = None
        self.prev_cursor_y = None

    def map_value_x(self, value):
        return self._map_value(value, self.input_range_x, (0, 640))

    def map_value_y(self, value):
        return self._map_value(value, self.input_range_y, (0, 480))

    def _map_value(self, value, input_range, output_range):
        input_min, input_max = input_range
        output_min, output_max = output_range
        mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
        mapped_value = max(min(mapped_value, output_max), output_min)
        return int(mapped_value)

    def process_frame(self, img, result):
        # RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # result = self.detector.process(RGB_frame)
        # hand_landmarks = result.multi_hand_landmarks[0] if result.multi_hand_landmarks else None
        
        hand_landmarks = result.multi_hand_landmarks[0] if result.multi_hand_landmarks else None

        if hand_landmarks:
            self.mp_drawing.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                                           self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                           self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))
            self.handle_landmarks(hand_landmarks, img)

        # # self.update_fps(img)
        # # img = cv2.flip(img, 1)
        # cv2.imshow("Imshow", img)

        return img

    def handle_landmarks(self, hand_landmarks, img):
        for id, landmark in enumerate(hand_landmarks.landmark):
            x = int(landmark.x * self.wCam)
            y = int(landmark.y * self.hCam)

            if id == 3:  # Thumb Knuckle
                self.handle_knuckle(x, y, img)
            elif id == 8:  # Index Finger
                self.index_x = self.screen_width - (x * self.screen_width / self.wCam)
                self.index_y = (self.screen_height / self.hCam * y)
            elif id == 12:  # Middle Finger
                self.mid_fing_x = self.screen_width - (x * self.screen_width / self.wCam)
                self.mid_fing_y = (self.screen_height / self.hCam * y)
                self.handle_double_click()

    def handle_knuckle(self, x, y, img):
        cv2.circle(img, (x, y), 20, (0, 255, 255))
        x = self.map_value_x(x)
        y = self.map_value_y(y)
        knuckle_x = self.screen_width - (x * self.screen_width / self.wCam)
        knuckle_y = self.screen_height / self.hCam * y

        if 0 < knuckle_x < self.screen_width and 0 < knuckle_y < self.screen_height:
            smoothed_x, smoothed_y = self.smooth_cursor(knuckle_x, knuckle_y)
            win32api.SetCursorPos((int(smoothed_x), int(smoothed_y)))
            self.prev_cursor_x = smoothed_x
            self.prev_cursor_y = smoothed_y
            self.handle_click(knuckle_y)

    def smooth_cursor(self, knuckle_x, knuckle_y):
        if self.prev_cursor_x is None or self.prev_cursor_y is None:
            return knuckle_x, knuckle_y
        smoothed_x = self.alpha * knuckle_x + (1 - self.alpha) * self.prev_cursor_x
        smoothed_y = self.alpha * knuckle_y + (1 - self.alpha) * self.prev_cursor_y
        return smoothed_x, smoothed_y

    def handle_click(self, knuckle_y):
        if abs(knuckle_y - self.index_y) < 50 and not self.left_click_flag:
            pyautogui.click()
            self.left_click_flag = True
            self.right_click_flag = False
        elif abs(knuckle_y - self.mid_fing_y) < 50 and not self.right_click_flag:
            pyautogui.click(button='right')
            self.right_click_flag = True
            self.left_click_flag = False
        else:
            self.left_click_flag = False
            self.right_click_flag = False

    def handle_double_click(self):
        if abs(self.index_x - self.mid_fing_x) < 20 and not self.right_click_flag and not self.left_click_flag:
            pyautogui.doubleClick()
            self.right_click_flag = True
            self.left_click_flag = False

    def update_fps(self, img):
        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # def run(self):
    #     while True:
    #         _, img = self.cap.read()
    #         self.process_frame(img)
    #         if cv2.waitKey(10) == ord('q'):
    #             break

    #     self.cap.release()
    #     cv2.destroyAllWindows()

if __name__ == "__main__":
    hand_tracker = HandTrackingMouseControl()
    hand_tracker.run()
