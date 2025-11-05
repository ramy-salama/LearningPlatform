from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Student(models.Model):
    GRADE_CHOICES = [
        ('primary', 'ابتدائي'),
        ('preparatory', 'إعدادي'),
        ('secondary', 'ثانوي'),
    ]
    
    YEAR_CHOICES = [
        ('first', 'الأول'),
        ('second', 'الثاني'),
        ('third', 'الثالث'),
        ('fourth', 'الرابع'),
        ('fifth', 'الخامس'),
        ('sixth', 'السادس'),
    ]
    
    # المعلومات الأساسية
    name = models.CharField('الاسم', max_length=100)
    phone_number = models.CharField('رقم الهاتف', max_length=11, unique=True)
    parent_phone = models.CharField('رقم ولي الأمر', max_length=11)
    
    # كلمة المرور - محسنة وآمنة
    password = models.CharField('كلمة المرور', max_length=128)  # تم زيادة الطول للتشفير
    
    residence = models.CharField('محل الإقامة', max_length=100)
    grade = models.CharField('المرحلة الدراسية', max_length=20, choices=GRADE_CHOICES)
    year = models.CharField('الصف/السنة', max_length=10, choices=YEAR_CHOICES)
    
    # نظام المحفظة الإلكترونية
    balance = models.DecimalField('رصيد المحفظة', max_digits=10, decimal_places=2, default=0)
    total_spent = models.DecimalField('إجمالي المنصرف', max_digits=10, decimal_places=2, default=0)
    bonus_balance = models.DecimalField('رصيد الإهداءات', max_digits=10, decimal_places=2, default=0)
    
    profile_image = models.ImageField('الصورة الشخصية', upload_to='students/', null=True, blank=True)
    created_at = models.DateTimeField('تاريخ التسجيل', auto_now_add=True)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """تشفير كلمة المرور قبل الحفظ"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """التحقق من كلمة المرور"""
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        """تأكد من تشفير كلمة المرور عند الحفظ"""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'طالب'
        verbose_name_plural = 'الطلاب'