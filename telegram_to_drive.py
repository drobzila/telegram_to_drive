import os
import json
from telethon import TelegramClient
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# Telegram
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel = os.getenv("TELEGRAM_CHANNEL")
session_file = 'telegram.session'

client = TelegramClient(session_file, api_id, api_hash)

# Google Drive
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
FOLDER_ID = os.getenv("GOOGLE_FOLDER")

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token"
)
drive_service = build('drive', 'v3', credentials=creds)

# سجل الفيديوهات التي تم رفعها لتجنب التكرار
LOG_FILE = 'uploaded_log.json'
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r') as f:
        uploaded = set(json.load(f))
else:
    uploaded = set()

async def main():
    channel_entity = await client.get_entity(channel)
    async for message in client.iter_messages(channel_entity, limit=20):  # آخر 20 رسالة
        if message.media and message.id not in uploaded:
            try:
                filename = await message.download_media()
                print(f"⬇️ Downloaded: {filename}")

                file_metadata = {'name': os.path.basename(filename), 'parents': [FOLDER_ID]}
                media = MediaFileUpload(filename)

                drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

                uploaded.add(message.id)
                print(f"✅ Uploaded: {filename}")

                # تحديث السجل مباشرة
                with open(LOG_FILE, 'w') as f:
                    json.dump(list(uploaded), f)

            except Exception as e:
                print(f"❌ Error with {message.id}: {e}")

with client:
    client.loop.run_until_complete(main())
