# Telegram to Google Drive

أداة Python لنقل الملفات المرسلة عبر Telegram إلى Google Drive، مع أدوات مساعدة لاختبار جلسة Telegram.

## المميزات
- استقبال/تنزيل الملفات من Telegram.
- رفع الملفات إلى Google Drive.
- استخدام جلسة Telegram محفوظة لإعادة الاتصال.
- سكربت اختبار للجلسة.

## التثبيت
```bash
git clone https://github.com/drobzila/telegram_to_drive.git
cd telegram_to_drive
pip install -r requirements.txt
```

## الإعداد
جهّز بيانات Telegram API وGoogle Drive وفق المتطلبات المستخدمة في السكربت، واحرص على عدم نشر session files أو مفاتيح API.

> **تحذير:** ملف `session.session` الموجود في المستودع قد يمثل جلسة دخول Telegram. يجب اعتباره سرًا حساسًا وعدم مشاركته أو نشره.

## التشغيل
```bash
python telegram_to_drive.py
```

لاختبار الجلسة:
```bash
python test_session.py
```

## الملفات
- `telegram_to_drive.py` — التطبيق الرئيسي.
- `test_session.py` — اختبار اتصال جلسة Telegram.
- `requirements.txt` — المتطلبات.
- `.github/` — إعدادات GitHub Actions.

## الترخيص
لم يتم تحديد ترخيص للمشروع بعد.
