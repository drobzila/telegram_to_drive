from telethon import TelegramClient
import os

# اسم ملف الجلسة
session_file = 'telegram.session'

# قراءة بيانات API من متغيرات البيئة
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH"))

client = TelegramClient(session_file, api_id, api_hash)

async def main():
    me = await client.get_me()
    print("تم تسجيل الدخول بنجاح!")
    print(f"اسم المستخدم: {me.username}")
    print(f"الاسم: {me.first_name} {me.last_name}")

with client:
    client.loop.run_until_complete(main())
