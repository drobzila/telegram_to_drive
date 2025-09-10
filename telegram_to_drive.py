import os
from telethon import TelegramClient
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# -------------------- 1. إعداد التلغرام --------------------
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel = os.getenv("TELEGRAM_CHANNEL")
session_path = os.getenv("TELEGRAM_SESSION_PATH", "./sessions/telegram.session")

client = TelegramClient(session_path, api_id, api_hash)


# -------------------- 2. إعداد Google Drive --------------------
def auth_gdrive():
    gauth = GoogleAuth()

    gauth.settings = {
        "client_config_backend": "settings",
        "client_config": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        },
        "save_credentials": True,
        "save_credentials_backend": "file",
        "save_credentials_file": "mycreds.txt",
        "get_refresh_token": True,
    }

    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # نستخدم الـ Refresh Token من GitHub Secrets
        gauth.credentials = {
            "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        }
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)


drive = auth_gdrive()


# -------------------- 3. تحميل من التلغرام ورفع إلى درايف --------------------
async def main():
    print("📥 جاري الاتصال بالتلغرام...")
    await client.start()

    async for message in client.iter_messages(channel, limit=3):  # آخر 3 فيديوهات
        if message.video:
            file_path = await message.download_media(file="./")
            print(f"✅ تم التحميل: {file_path}")

            gfile = drive.CreateFile({
                "title": os.path.basename(file_path),
                "parents": [{"id": os.getenv("GOOGLE_FOLDER_ID")}],
            })
            gfile.SetContentFile(file_path)
            gfile.Upload()
            print(f"☁️ تم الرفع إلى Google Drive: {file_path}")


with client:
    client.loop.run_until_complete(main())
