import os
from telethon import TelegramClient
import ffmpeg
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

# =============================
# إعدادات Telegram
# =============================
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
session_file = "telegram.session"
channel_username = os.getenv("TELEGRAM_CHANNEL")  # معرف القناة أو اسم المستخدم

# =============================
# إعدادات Google Drive
# =============================
gdrive_folder_id = os.getenv("GOOGLE_FOLDER_ID")  # مجلد الرفع
log_file = "uploaded_log.txt"
max_uploads = 20  # عدد الفيديوهات المطلوب رفعها

# =============================
# المصادقة على Google Drive
# =============================
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")  # يجب حفظ التوكن مرة واحدة يدويا
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)

# =============================
# تحميل سجل الملفات السابقة
# =============================
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        uploaded_files = set(line.split(" | ")[0] for line in f.read().splitlines())
else:
    uploaded_files = set()

# =============================
# دالة رفع الفيديو إلى Drive
# =============================
def upload_to_drive(file_path, file_name, duration):
    gfile = drive.CreateFile({"parents": [{"id": gdrive_folder_id}], "title": file_name})
    gfile.SetContentFile(file_path)
    gfile.Upload()
    print(f"Uploaded: {file_name} ({duration:.1f}s)")
    uploaded_files.add(file_name)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{file_name} | {duration:.1f}s | {datetime.now()}\n")

# =============================
# تنفيذ Telegram Client
# =============================
client = TelegramClient(session_file, api_id, api_hash)

async def main():
    await client.start()
    channel = await client.get_entity(channel_username)

    uploaded_count = 0
    async for message in client.iter_messages(channel, limit=200):  # جلب 200 رسالة مثلاً
        if uploaded_count >= max_uploads:
            break

        if message.video:
            file_name = message.file.name or f"{message.id}.mp4"
            if file_name in uploaded_files:
                print(f"Already uploaded: {file_name}")
                continue

            temp_path = f"temp_{message.id}.mp4"
            try:
                await message.download_media(file=temp_path)

                # استخراج مدة الفيديو باستخدام ffmpeg
                probe = ffmpeg.probe(temp_path)
                duration = float(probe["format"]["duration"])

                if duration < 60:  # أقل من دقيقة
                    upload_to_drive(temp_path, file_name, duration)
                    uploaded_count += 1
                    if uploaded_count >= max_uploads:
                        break
                else:
                    print(f"Skipping (long video {duration:.1f}s): {file_name}")

            except Exception as e:
                print(f"Error processing {file_name}: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    print(f"\n✅ تم رفع {uploaded_count} فيديو إلى Google Drive")

with client:
    client.loop.run_until_complete(main())
