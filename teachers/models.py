from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Teacher(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'بكالوريوس'),
        ('master', 'ماجستير'),
        ('phd', 'دكتوراه'),
    ]
    
    TEACHING_LEVEL_CHOICES = [
        ('primary', 'المرحلة الابتدائية'),
        ('preparatory', 'المرحلة الإعدادية'),
        ('secondary', 'المرحلة الثانوية'),
    ]

    PAYMENT_METHODS = [
        ('vodafone_cash', 'فودافون كاش'),
        ('insta_pay', 'انستا باي'),
    ]
    
    # المعلومات الشخصية
    name = models.CharField('الاسم', max_length=100)
    phone_number = models.CharField('رقم الهاتف', max_length=11, unique=True)
    email = models.EmailField('البريد الإلكتروني')
    
    # كلمة المرور - محسنة وآمنة
    password = models.CharField('كلمة المرور', max_length=128)  # تم زيادة الطول للتشفير
    
    address = models.CharField('العنوان', max_length=200)
    bio = models.TextField('السيرة الذاتية')
    specialization = models.CharField('التخصص', max_length=100)
    
    # المراحل التعليمية - محسنة للتحقق
    teaching_levels = models.CharField(
        'المراحل التعليمية', 
        max_length=100, 
        help_text='اختر المراحل التي تدرسها (اضغط Ctrl لاختيار أكثر من واحدة)'
    )
    
    experience = models.TextField('الخبرات السابقة')
    degree = models.CharField('المؤهل العلمي', max_length=20, choices=DEGREE_CHOICES)
    major = models.CharField('التخصص الدقيق', max_length=100)
    certificates = models.TextField('الشهادات الإضافية', blank=True)
    
    # الحقول الجديدة - الصور
    profile_image = models.ImageField(
        'الصورة الشخصية', 
        upload_to='teachers/profiles/', 
        default='default_profile.jpg'
    )
    certificate_image = models.ImageField(
        'صورة الشهادة', 
        upload_to='teachers/certificates/', 
        default='default_certificate.jpg'
    )
    
    profit_percentage = models.IntegerField('نسبة الأرباح', default=50)
    
    # معلومات الدفع
    payment_method = models.CharField('طريقة الاستلام', max_length=20, choices=PAYMENT_METHODS)
    account_number = models.CharField('رقم الحساب/المحفظة', max_length=100)
    
    # حالة المعلم
    status = models.CharField(
        'الحالة', 
        max_length=20, 
        default='pending', 
        choices=[
            ('pending', 'قيد الانتظار'),
            ('approved', 'مقبول'),
            ('rejected', 'مرفوض')
        ]
    )
    
    created_at = models.DateTimeField('تاريخ التسجيل', auto_now_add=True)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """تشفير كلمة المرور قبل الحفظ"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """التحقق من كلمة المرور"""
        return check_password(raw_password, self.password)

    def get_teaching_levels_list(self):
        """الحصول على قائمة المراحل التعليمية"""
        if self.teaching_levels:
            return self.teaching_levels.split(',')
        return []

    def save(self, *args, **kwargs):
        """تأكد من تشفير كلمة المرور عند الحفظ"""
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'معلم'
        verbose_name_plural = 'المعلمين'