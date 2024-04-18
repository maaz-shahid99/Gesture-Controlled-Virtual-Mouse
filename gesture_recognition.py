import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)


BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a gesture recognizer instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result.hand_landmarks))


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='C:\\Users\\maazs\\OneDrive\\Documents\\Projects\\Virtual Mouse\\models\\gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
    )


with GestureRecognizer.create_from_options(options) as recognizer:
  # The detector is initialized. Use it here.
  # ...
    print('gesture recognizer created')

    while True:

        success, img = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue 

        RGB_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=RGB_frame)
        
        # Get the current time in seconds since the epoch
        current_time_ms = int(time.time() * 1000)
        
        detected_ges = recognizer.recognize_async(mp_image, current_time_ms)

        # print(detected_ges)

        cv2.imshow("Imshow", img)

        if cv2.waitKey(10) == ord('q'):
            break