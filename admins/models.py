# admins/models.py - مع إنشاء مسؤول افتراضي تلقائي
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Admin(models.Model):
    PERMISSION_CHOICES = [
        ('student_manager', 'مشرف الطلاب'),
        ('teacher_manager', 'مشرف المعلمين'),
        ('course_manager', 'مشرف الكورسات'),
        ('support_manager', 'مشرف الدعم الفني'),
        ('super_admin', 'المدير العام'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=11)
    profile_image = models.ImageField(upload_to='admins/', null=True, blank=True)
    permissions = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """تشفير كلمة المرور قبل الحفظ"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """التحقق من كلمة المرور"""
        return check_password(raw_password, self.password)

    def has_permission(self, permission_code):
        """التحقق من صلاحية معينة"""
        return self.permissions == permission_code or self.permissions == 'super_admin'

    def is_super_admin(self):
        """التحقق إذا كان مدير عام"""
        return self.permissions == 'super_admin'

    def can_manage_students(self):
        """التحقق من صلاحية إدارة الطلاب"""
        return self.has_permission('student_manager') or self.is_super_admin()

    def can_manage_teachers(self):
        """التحقق من صلاحية إدارة المعلمين"""
        return self.has_permission('teacher_manager') or self.is_super_admin()

    def can_manage_courses(self):
        """التحقق من صلاحية إدارة الكورسات"""
        return self.has_permission('course_manager') or self.is_super_admin()

    def save(self, *args, **kwargs):
        """تأكد من تشفير كلمة المرور عند الحفظ"""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'مسؤول'
        verbose_name_plural = 'المسؤولين'

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """إنشاء مسؤول افتراضي تلقائياً بعد الهجرة"""
    if sender.name == 'admins':
        try:
            if not Admin.objects.filter(email="admin@eduplatform.com").exists():
                admin = Admin(
                    name="المسؤول الرئيسي",
                    email="admin@eduplatform.com",
                    password="admin123",
                    phone_number="01002150057",
                    permissions="super_admin"
                )
                admin.save()
                print("✅ تم إنشاء المسؤول الافتراضي تلقائياً")
        except Exception as e:
            print(f"⚠️ لم يتم إنشاء المسؤول الافتراضي: {e}")