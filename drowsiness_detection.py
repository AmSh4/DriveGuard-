import cv2
import os
import numpy as np
from keras.models import load_model
from pygame import mixer
import datetime
import requests

# Initialize pygame mixer
mixer.init()

# Load the alarm sound
sound = mixer.Sound('alarm.wav')

# Load Haar cascades for face and eyes detection
face = cv2.CascadeClassifier('haar cascade files/haarcascade_frontalface_alt.xml')
leye = cv2.CascadeClassifier('haar cascade files/haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier('haar cascade files/haarcascade_righteye_2splits.xml')

# Define labels for eye state (Closed/Open)
lbl = ['Close', 'Open']

# Load the CNN model for eye state prediction
model = load_model('models/cnncat2.h5')

# Get the current working directory
path = os.getcwd()

# Open the default camera (Webcam)
cap = cv2.VideoCapture(0)

# Define font for text overlay
font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# Initialize variables for counting frames, keeping score, and setting threshold thickness
count = 0
score = 0
thicc = 2

# Initialize prediction arrays for left and right eyes
rpred = [99]
lpred = [99]

alarm_triggered = False
user_name = None  # Store user name

def save_alarm_snapshot():
    global alarm_triggered
    if not alarm_triggered:
        # Get the current time
        current_time = datetime.datetime.now()
        # Format the time as required
        time_formatted = current_time.strftime("%I-%M-%S_%p")  # Example: 03-45-21_PM
        # Create the folder name based on the current date
        folder_name = current_time.strftime("%Y-%m-%d")
        # Create the folder if it doesn't exist
        folder_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'drowsiness_detection', folder_name)
        os.makedirs(folder_path, exist_ok=True)
        # Save the snapshot with the time information
        snapshot_path = os.path.join(folder_path, f'snapshot_{time_formatted}.jpg')
        cv2.imwrite(snapshot_path, frame)
        # Create a text file with the time information
        with open(os.path.join(folder_path, 'alarm_times.txt'), 'a') as f:
            f.write(f'Alarm beeped at: {current_time.strftime("%I:%M %p")}\n')
        alarm_triggered = True
        # Notify the Flask server that the alarm is triggered
        requests.get('http://127.0.0.1:5000/set_alarm_triggered')

# Start the main loop for video capture and processing
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    height, width = frame.shape[:2]

    # Convert frame to grayscale for better face and eye detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))

    # Detect left and right eyes separately
    left_eye = leye.detectMultiScale(gray)
    right_eye = reye.detectMultiScale(gray)

    # Draw rectangle at the bottom for displaying text
    cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 1)

    # Process each detected right eye
    for (x, y, w, h) in right_eye:
        r_eye = frame[y:y + h, x:x + w]
        count += 1

        # Preprocess the right eye image for input to the model
        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (24, 24))
        r_eye = r_eye / 255
        r_eye = r_eye.reshape(24, 24, -1)
        r_eye = np.expand_dims(r_eye, axis=0)
        rpred = (model.predict(r_eye) > 0.5).astype("int32")

        # Assign label based on prediction
        if np.any(rpred[0] == 1):
            lbl = 'Open'
        if np.any(rpred[0] == 0):
            lbl = 'Closed'
        break

    # Process each detected left eye
    for (x, y, w, h) in left_eye:
        l_eye = frame[y:y + h, x:x + w]
        count += 1

        # Preprocess the left eye image for input to the model
        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (24, 24))
        l_eye = l_eye / 255
        l_eye = l_eye.reshape(24, 24, -1)
        l_eye = np.expand_dims(l_eye, axis=0)

        # Predict the state of the left eye
        lpred = (model.predict(l_eye) > 0.5).astype("int32")

        # Assign label based on prediction
        if np.any(lpred[0] == 1):
            lbl = 'Open'
        if np.any(lpred[0] == 0):
            lbl = 'Closed'
        break

    # Check if both eyes are closed
    if rpred[0][0] == 0 and lpred[0][0] == 0:  # Both eyes open
        score -= 1
        cv2.putText(frame, "Open", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    else:
        score += 1
        cv2.putText(frame, "Closed", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Ensure score does not go below 0
    if score < 0:
        score = 0
    cv2.putText(frame, 'Score:' + str(score), (100, height - 20), font, 1, (255, 255, 255),1, cv2.LINE_AA)

    # Check if score exceeds threshold, indicating drowsiness
    if score > 15:
        # Person is feeling sleepy, so we beep the alarm and save frame with overlay indicating drowsiness
        cv2.imwrite(os.path.join(path, 'image.jpg'), frame)
        try:
            # Play alarm sound
            sound.play()
            save_alarm_snapshot()
            # Save the user's name when drowsiness is detected
            requests.post('http://127.0.0.1:5000/set_drowsy_user', json={"name": user_name})
        except:  # isplaying = False
            pass

        # Adjust rectangle thickness for visual alert
        if thicc < 16:
            thicc += 2
        else:
            thicc -= 2
            if thicc < 2:
                thicc = 2

        # Draw red rectangle around frame for visual alert
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), thicc)

    # Display the processed frame
    cv2.imshow('frame', frame)

    # Check for 'q' key to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

