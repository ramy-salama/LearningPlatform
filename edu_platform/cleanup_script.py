# cleanup_script.py - تشغيل هذا السكربت لتنظيف البيانات
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_platform.settings')
django.setup()

def cleanup_data():
    """تنظيف البيانات القديمة وإنشاء مسؤول افتراضي"""
    try:
        from messaging.models import Message
        from admins.models import Admin
        
        print("🔄 بدء عملية تنظيف البيانات...")
        
        # 1. حذف جميع الرسائل القديمة
        message_count = Message.objects.count()
        Message.objects.all().delete()
        print(f"✅ تم حذف {message_count} رسالة قديمة")
        
        # 2. إنشاء مسؤول افتراضي إذا لم يكن موجوداً
        if not Admin.objects.filter(email="admin@eduplatform.com").exists():
            admin = Admin(
                name="المسؤول الرئيسي",
                email="admin@eduplatform.com",
                password="admin123",
                phone_number="01000000001",
                permissions="super_admin"
            )
            admin.save()
            print("✅ تم إنشاء المسؤول الافتراضي")
        else:
            print("✅ المسؤول الافتراضي موجود بالفعل")
        
        print("🎉 تم الانتهاء من عملية التنظيف بنجاح!")
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء التنظيف: {e}")

if __name__ == "__main__":
    cleanup_data()