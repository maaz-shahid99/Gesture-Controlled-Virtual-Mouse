import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Callback function to print gesture recognition results
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    if result.gestures:
        # Get the category name of the recognized gesture
        category_name = result.gestures[0][0].category_name
        print(category_name)
    else:
        print("None")  # Print 'None' when no gestures are recognized

# Initialize MediaPipe drawing utils and hands module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Configure options for the gesture recognizer
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='D:\web development\Gesture-Controlled-Virtual-Mouse\models\gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

# Create a gesture recognizer instance
with GestureRecognizer.create_from_options(options) as recognizer:
    print('Gesture recognizer created')

    with mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            success, img = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Convert BGR image to RGB for MediaPipe processing
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Detect hand landmarks using MediaPipe Hands
            results = hands.process(rgb_img)

            if results.multi_hand_landmarks:
                if len(results.multi_hand_landmarks) == 2:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks on the image with specified color and thickness
                        mp_drawing.draw_landmarks(
                            img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                        )

                    # Prepare image for gesture recognition
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
                    current_time_ms = int(time.time() * 1000)

                    # Perform gesture recognition on the processed image
                    recognizer.recognize_async(mp_image, current_time_ms)
                else:
                    print("None")  # Print 'None' when only one hand is detected
            else:
                print("None")  # Print 'None' when no hands are detected

            img = cv2.flip(img, 1)  # Flip the image horizontally
            cv2.imshow("Imshow", img)

            if cv2.waitKey(10) == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()
