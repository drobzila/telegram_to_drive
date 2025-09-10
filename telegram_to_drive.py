import os
import asyncio
from telethon import TelegramClient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ===== إعدادات التلغرام =====
api_id = 27874350
api_hash = "a8cca90ec7d1023b8118163822f187c0"
session_file = "9629a04d-33ed-4626-b130-155b39ee9a93.session"  # ملف الجلسة
channel = "quranbng"
download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

# ===== بيانات Google OAuth =====
CLIENT_ID = "553805965519-1gvas0tmcl86v76k7m9bhkmc7m76657s.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//09SLS4A1oZYsJCgYIARAAGAkSNwF-L9IrQJneNmOVOAjihJWVMGFL2gYlLAdg0Y_0SZg4bQPjbRR-qkDKYvbSS4weE7zrPh8w4_E"
FOLDER_ID = "1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ"

SCOPES = ["https://www.googleapis.com/auth/drive"]

# إنشاء بيانات الاعتماد
creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=SCOPES,
)
creds.refresh(Request())
drive_service = build("drive", "v3", credentials=creds)

# ===== تحميل الفيديوهات من التلغرام =====
async def download_videos():
    client = TelegramClient(session_file, api_id, api_hash)
    await client.start()  # يستخدم ملف الجلسة مباشرة

    async for message in client.iter_messages(channel, limit=20):
        if message.video and message.file.size <= 7 * 1024 * 1024:  # أقل من 7MB
            filename = message.file.name or f"{message.id}.mp4"
            filepath = os.path.join(download_dir, filename)

            print(f"⬇️ Downloading: {filename}")
            await message.download_media(file=filepath)
            print(f"✅ Saved locally: {filepath}")

            # رفع الفيديو إلى Google Drive
            file_metadata = {"name": filename, "parents": [FOLDER_ID]}
            media = MediaFileUpload(filepath, resumable=True)
            drive_service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            print(f"☁️ Uploaded to Drive: {filename}")

    await client.disconnect()

asyncio.run(download_videos())
