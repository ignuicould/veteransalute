import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
drawing_utils = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)

# Initialize webcam
cap = cv2.VideoCapture(0)

def is_saluting(landmarks):
    # Check if the hand is raised by examining the y-coordinates of certain landmarks
    if landmarks:
        wrist_y = landmarks[mp_hands.HandLandmark.WRIST].y
        index_finger_tip_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        thumb_tip_y = landmarks[mp_hands.HandLandmark.THUMB_TIP].y

        # Simple heuristic: If the index finger tip is significantly higher than the wrist
        return index_finger_tip_y < wrist_y and thumb_tip_y < wrist_y
    return False

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # Draw the hand annotations on the image
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS, drawing_utils, drawing_utils)

            if is_saluting(landmarks.landmark):
                cv2.putText(image, 'Saluting Detected!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the image
    cv2.imshow('MediaPipe Hands', image)

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
