import cv2
import mediapipe as mp
import time
import ctypes
import struct
import array
import win32gui
from win32con import WM_COPYDATA as WM_COPYDATA     # int 74

# Initialize MediaPipe Hands and Drawing Utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
drawing_utils = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Variables for tracking salute duration
salute_start_time = None
salute_held = False
required_duration = 3  # seconds

def convertCharArrayToLPCWSTR(charArray):
    wString = ctypes.create_unicode_buffer(charArray)
    return wString

WIN_CLASS = "TForm1"
hwnd = win32gui.FindWindow(WIN_CLASS, None)
DW_DATA = ctypes.windll.user32.RegisterWindowMessageW(convertCharArrayToLPCWSTR("SendCursorCoord"))

def is_army_salute(landmarks):
    if landmarks:
        # Extract relevant landmarks
        wrist = landmarks[mp_hands.HandLandmark.WRIST]
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        index_finger_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_finger_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

        # Define y-coordinates for the landmarks
        wrist_y = wrist.y
        thumb_y = thumb_tip.y
        index_finger_y = index_finger_tip.y
        middle_finger_y = middle_finger_tip.y

        # Heuristic conditions for an army salute:
        salute_threshold = 0.3
        hand_to_forehead_threshold = 0.5

        hand_is_high = (thumb_y < wrist_y - salute_threshold and 
                        index_finger_y < wrist_y - salute_threshold and 
                        middle_finger_y < wrist_y - salute_threshold)
        hand_near_forehead = wrist_y < hand_to_forehead_threshold

        return hand_is_high and hand_near_forehead
    return False

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
        salute_detected = False
        for landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS, drawing_utils, drawing_utils)
            if is_saluting(landmarks.landmark):
                salute_detected = True
                if salute_start_time is None:
                    salute_start_time = time.time()  # Start timing
                elif time.time() - salute_start_time >= required_duration:
                    salute_held = True
                    cv2.putText(image, 'Salute Held for 3 Seconds!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    if hwnd == 0:
                        print("Window not found!")
                    else:
                        #print("Window found!")
                        data_to_send = b'x:50|y:50&'
                        
                        buffer = array.array('u', data_to_send)
                        buffer_address, buffer_length = buffer.buffer_info()
                        copy_struct = struct.pack('PLP', DW_DATA, buffer_length*buffer.itemsize, buffer_address)
                        response = win32gui.SendMessage(hwnd, WM_COPYDATA, hwnd, copy_struct)
                        
                        #print("Response: ", response)
                        salute_start_time = None
            else:
                salute_start_time = None  # Reset timer if not saluting
    else:
        salute_start_time = None

    # Display the image
    cv2.imshow('Salute The Troops', image)

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
