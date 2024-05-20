import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

finger_tips = [8, 12, 16, 20]
thumb_tip = 4

def is_open_palm(lm_list):
    # Check if all fingers are extended
    return all(lm_list[tip].y < lm_list[tip - 2].y for tip in finger_tips)

def is_victory_gesture(lm_list):
    # Index and middle finger tips
    index_tip = lm_list[8]
    middle_tip = lm_list[12]

    # Victory gesture logic (V shape with index and middle fingers)
    return (index_tip.y < lm_list[6].y and
            middle_tip.y < lm_list[10].y)

def is_closed_fist(lm_list):
    # Check if all fingers are closed
    return all(lm_list[tip].y > lm_list[tip - 2].y for tip in finger_tips)

while True:
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.flip(img, 1)
    h, w, c = img.shape
    results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    gesture_label_right = ""  # No label by default
    gesture_label_left = ""   # No label by default

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                lm_list.append(lm)

            # Default to "None" if no recognized gesture is detected
            gesture_detected = False

            if is_open_palm(lm_list):
                if lm_list[0].x < 0.5:
                    gesture_label_left = "Open Palm"
                else:
                    gesture_label_right = "Open Palm"
                gesture_detected = True

            elif is_victory_gesture(lm_list):
                if lm_list[0].x < 0.5:
                    gesture_label_left = "Victory"
                else:
                    gesture_label_right = "Victory"
                gesture_detected = True

            elif is_closed_fist(lm_list):
                if lm_list[0].x < 0.5:
                    gesture_label_left = "Closed Fist"
                else:
                    gesture_label_right = "Closed Fist"
                gesture_detected = True

            if not gesture_detected:
                if lm_list[0].x < 0.5:
                    gesture_label_left = "None"
                else:
                    gesture_label_right = "None"

            # Draw landmarks on the hand
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display gesture labels at the top corners if a gesture is detected or set to "None"
    if gesture_label_right:
        text_size_right = cv2.getTextSize(gesture_label_right, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)[0]
        cv2.putText(img, gesture_label_right, (w - text_size_right[0] - 10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    if gesture_label_left:
        text_size_left = cv2.getTextSize(gesture_label_left, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)[0]
        cv2.putText(img, gesture_label_left, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Hand Gesture Recognition", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
