# WhatsApp Link Scanner

نظام متكامل لاستكشاف روابط WhatsApp من مصادر Telegram، فحص صلاحيتها، وتصنيفها.

## الميزات

- 🔍 استكشاف روابط WhatsApp من مجموعات وقنوات Telegram
- ✅ فحص صلاحية الروابط وتصنيفها (مباشر، طلب انضمام، غير صالح)
- 💼 حفظ الروابط في محفظة المستخدم
- 📤 تصدير الروابط بصيغ TXT، CSV، JSON
- 📱 إرسال الروابط إلى WhatsApp
- 📊 إدارة المهام والمحفظة
- 🔐 أمان متكامل للجلسات والبيانات

## المتطلبات

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (اختياري)

## التثبيت

### باستخدام Docker

```bash
# نسخ المشروع
git clone <repository-url>
cd whatsapp_link_scanner

# إنشاء ملف البيئة
cp .env.example .env
# تعديل .env بالبيانات الصحيحة

# بناء وتشغيل
make docker-build
make docker-up