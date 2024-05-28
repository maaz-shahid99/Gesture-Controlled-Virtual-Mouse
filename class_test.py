import cv2
import time
import mediapipe as mp
import pyautogui
import win32api
import utils

class HandDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.wCam, self.hCam = 640, 480
        self.screen_width, self.screen_height = pyautogui.size()
        self.pTime = time.time()  # Correct initialization here

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
        self.mid_fing_x = 0
        self.mid_fing_y = 0

        self.left_click_flag = False
        self.right_click_flag = False

        self.cursor_res_x = 240
        self.cursor_res_y = 180

        self.input_range_x = (int((self.wCam - self.cursor_res_x) / 2),
                              int(self.cursor_res_x + (self.wCam - self.cursor_res_x) / 2))
        self.input_range_y = (int((self.hCam - self.cursor_res_y) / 2),
                              int(self.cursor_res_y + (self.hCam - self.cursor_res_y) / 2))

        self.alpha = 0.3
        self.prev_cursor_x = None
        self.prev_cursor_y = None

    def find_hand_landmarks(self):
        _, img = self.cap.read()
        RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.detector.process(RGB_frame)
        return img, result

    def run(self):
        while True:
            img, result = self.find_hand_landmarks()
            self.display_FPS(img)
            self.draw_hand_connections(img, result)
            cv2.imshow("Imshow", img)
            if cv2.waitKey(10) == ord('q'):
                break

    def draw_hand_connections(self, img, result):
        hand_landmarks = None
        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                                            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2,
                                                                        circle_radius=2),
                                            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2,
                                                                        circle_radius=2))
        self.detect_cursor_clicks(img, hand_landmarks)

    def detect_cursor_clicks(self, img, hand_landmarks):
        if hand_landmarks:
            for id, landmark in enumerate(hand_landmarks.landmark):
                x = int(landmark.x * self.wCam)
                y = int(landmark.y * self.hCam)

                if id == 3:  # Thumb Knuckle
                    cv2.circle(img=img, center=(x, y), radius=20, color=(0, 255, 255))
                    # x = self.map_value_x(x)
                    # y = self.map_value_y(y)

                    x = utils.map_value_x(x)
                    y = utils.map_value_y(y)

                    knuckle_x = self.screen_width - (x * self.screen_width / self.wCam)
                    knuckle_y = self.screen_height / self.hCam * y

                    if 0 < knuckle_x < self.screen_width and 0 < knuckle_y < self.screen_height:
                        if self.prev_cursor_x is None or self.prev_cursor_y is None:
                            smoothed_x = knuckle_x
                            smoothed_y = knuckle_y
                        else:
                            smoothed_x = self.alpha * knuckle_x + (1 - self.alpha) * self.prev_cursor_x
                            smoothed_y = self.alpha * knuckle_y + (1 - self.alpha) * self.prev_cursor_y

                        win32api.SetCursorPos((int(smoothed_x), int(smoothed_y)))

                        self.prev_cursor_x = smoothed_x
                        self.prev_cursor_y = smoothed_y

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

                if id == 8:  # Index Finger
                    cv2.circle(img=img, center=(x, y), radius=20, color=(0, 255, 255))
                    self.index_x = (self.screen_width - (x * self.screen_width / self.wCam))
                    self.index_y = (self.screen_height / self.hCam * y)

                if id == 12:  # Middle Finger
                    cv2.circle(img=img, center=(x, y), radius=20, color=(0, 255, 255))
                    self.mid_fing_x = self.screen_width - (x * self.screen_width / self.wCam)
                    self.mid_fing_y = self.screen_height / self.hCam * y

                    if abs(self.index_x - self.mid_fing_x) < 20 and not self.right_click_flag and not self.left_click_flag:
                        print('double click')
                        pyautogui.doubleClick()
                        self.right_click_flag = True
                        self.left_click_flag = False

    def display_FPS(self, img):
        # Frame Rate
        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime

        # Flip Image
        img = cv2.flip(img, 1)
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

if __name__ == "__main__":
    hand_detector = HandDetector()
    hand_detector.run()