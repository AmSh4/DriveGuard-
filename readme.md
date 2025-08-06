# DRIVEGUARD : Drowsiness Detection Using Deep Learning

This project detects drowsiness in real-time using a webcam feed by monitoring eye states with a CNN (Convolutional Neural Network) model. When prolonged eye closure is detected, an alarm is triggered to alert the user.


---

## 📌 Features

Real-time detection of drowsiness using a webcam

Eye state classification using a trained deep learning model

Audio alert system for detected drowsiness

Time logging for drowsiness events

Clean UI using OpenCV for frame annotations



---

## 🧠 Technologies Used

Python 3

  OpenCV – for real-time image processing

  Keras – for loading the pre-trained CNN model

  NumPy – for array operations

  Pygame – for playing alert sounds



---

## 🗂️ Project Structure

     drowsiness_detection/
     ├── drowsiness_detection.py       # Main script
     ├── model.h5                      # Trained eye state CNN model
     ├── alarm.wav                     # Alarm sound
     ├── shape_predictor_68_face.dat   # dlib facial landmark predictor
     ├── README.md                     # Project documentation


---

## ⚙️ How to Run

### 1. Clone the repository:

    git clone 
    https://github.com/AmSh4/DriveGuard-.git
    cd DriveGuard-


### 2. Install the dependencies:

    pip install opencv-python keras pygame numpy


### 3. Ensure these files are present:

    model.h5
    shape_predictor_68_face.dat
    alarm.wav



### 4. Run the script:

    python drowsiness_detection.py




---

## 🧪 How It Works

Facial landmarks are detected using dlib’s 68-point predictor.

The region of interest (ROI) for eyes is extracted from the video frame.

The CNN model predicts whether eyes are open or closed.

If eyes are detected closed for consecutive frames (can edit the time), an alarm is triggered.



---

## ✅ Ideal Use Cases

Driver drowsiness detection systems

Workplace safety monitoring

Assistive systems for fatigue-prone tasks
