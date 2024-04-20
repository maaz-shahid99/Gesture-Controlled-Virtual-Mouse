import cv2
import mediapipe as mp
import time

class GestureRecognizerWrapper:
    def __init__(self, model_asset_path):
        self.options = self._create_options(model_asset_path)
        self.recognizer = None

    def _create_options(self, model_asset_path):
        base_options = mp.tasks.BaseOptions(model_asset_path=model_asset_path)
        return mp.tasks.vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            result_callback=self.print_result
        )

    def print_result(self, result: mp.tasks.vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        if result.gestures:
            category_name = result.gestures[0][0].category_name
            print(category_name)
        else:
            print("No gestures recognized")

    def create_recognizer(self):
        self.recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(self.options)
        print('Gesture recognizer created')

    def recognize_gestures(self, frame, current_time_ms):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        return self.recognizer.recognize_async(mp_image, current_time_ms)

class CameraCapture:
    def __init__(self, device_index=0):
        self.cap = cv2.VideoCapture(device_index)

    def read_frame(self):
        success, img = self.cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            return None
        return img

    def release(self):
        self.cap.release()

def main():
    model_path = 'C:\\Users\\maazs\\OneDrive\\Documents\\Projects\\Virtual Mouse\\models\\gesture_recognizer.task'
    gesture_recognizer = GestureRecognizerWrapper(model_path)
    gesture_recognizer.create_recognizer()

    camera = CameraCapture(0)

    while True:
        frame = camera.read_frame()
        if frame is None:
            continue

        current_time_ms = int(time.time() * 1000)
        detected_gestures = gesture_recognizer.recognize_gestures(frame, current_time_ms)

        cv2.imshow("Imshow", frame)

        if cv2.waitKey(10) == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
