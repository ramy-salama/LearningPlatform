from django.db import models
from teachers.models import Teacher
from students.models import Student
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import os # ✅ إضافة os للاستخدام في التشفيرse64

class Course(models.Model):
    TEACHER_PERCENTAGE_CHOICES = [
        (50, '50% - حتى 50 طالب'),
        (60, '60% - من 51 إلى 100 طالب'),
        (70, '70% - أكثر من 100 طالب'),
    ]

    LANGUAGE_CHOICES = [
        ('ar', 'عربي'),
        ('en', 'English'),
    ]

    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('disabled', 'معطل'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="المعلم")
    title = models.CharField(max_length=200, verbose_name="عنوان الكورس")
    description = models.TextField(verbose_name="وصف تفصيلي")
    category = models.CharField(max_length=100, verbose_name="التصنيف والتخصص")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الكورس")
    image = models.ImageField(upload_to='courses/images/', verbose_name="الصورة الرئيسية")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, verbose_name="لغة العرض")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البدء")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    estimated_duration = models.CharField(max_length=100, verbose_name="المدة الزمنية المقدرة")
    prerequisites = models.TextField(blank=True, verbose_name="المتطلبات المسبقة")
    teacher_percentage = models.IntegerField(choices=TEACHER_PERCENTAGE_CHOICES, default=50, verbose_name="نسبة المعلم")
    students_count = models.IntegerField(default=0, verbose_name="عدد الطلاب المسجلين")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="متوسط التقييم")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'كورس'
        verbose_name_plural = 'الكورسات'


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200, verbose_name="عنوان الوحدة")
    description = models.TextField(blank=True, verbose_name="وصف الوحدة")
    order = models.IntegerField(default=0, verbose_name="ترتيب الوحدة")

    class Meta:
        ordering = ['order']
        verbose_name = 'وحدة دراسية'
        verbose_name_plural = 'الوحدات الدراسية'

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'درس فيديو'),
        ('text', 'مواد نصية'),
        ('file', 'ملفات مرفقة'),
        ('project', 'مشروع تطبيقي'),
        ('resource', 'موارد إضافية'),
    ]

    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200, verbose_name="عنوان الدرس")
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, verbose_name="نوع الدرس")
    content = models.TextField(blank=True, verbose_name="المحتوى النصي")
    video_url = models.URLField(blank=True, verbose_name="رابط الفيديو")
    youtube_video_id = models.CharField(max_length=50, blank=True, verbose_name="YouTube Video ID")
    encrypted_video_id = models.TextField(blank=True, verbose_name="معرف الفيديو المشفر")
    attachment = models.FileField(upload_to='courses/attachments/', blank=True, null=True, verbose_name="ملف مرفق")
    external_link = models.URLField(blank=True, verbose_name="رابط خارجي")
    order = models.IntegerField(default=0, verbose_name="ترتيب الدرس")
    duration = models.IntegerField(default=0, verbose_name="مدة الدرس (دقائق)")

    class Meta:
        ordering = ['order']
        verbose_name = 'درس'
        verbose_name_plural = 'الدروس'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """تشفير Video ID تلقائياً عند الحفظ"""
        if self.youtube_video_id and not self.encrypted_video_id:
            self.encrypted_video_id = self.encrypt_video_id(self.youtube_video_id)
        super().save(*args, **kwargs)

    def encrypt_video_id(self, video_id):
        """تشفير Video ID"""
        try:
            # ⬇️ تأكد من أن المفتاح صالح
            ENCRYPTION_KEY = os.environ.get('FERNET_KEY', 'A_VERY_INSECURE_DEFAULT_KEY_FOR_DEMO_ONLY') # ✅ يجب تغيير القيمة الافتراضية في الإنتاج
            fernet = Fernet(ENCRYPTION_KEY)
            encrypted = fernet.encrypt(video_id.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            # ⬇️ لو فشل التشفير، ارجع الـ video_id كما هو
            print(f"Encryption error: {e}")
            return video_id

    def decrypt_video_id(self):
        """فك تشفير Video ID"""
        if not self.encrypted_video_id:
            return self.youtube_video_id  # ⬅️ ارجع الـ ID الأصلي
            
        try:
            fernet = Fernet(settings.ENCRYPTION_KEY)
            decoded = base64.urlsafe_b64decode(self.encrypted_video_id.encode())
            return fernet.decrypt(decoded).decode()
        except Exception as e:
            # ⬇️ لو فشل فك التشفير، ارجع الـ ID الأصلي
            print(f"Decryption error: {e}")
            return self.youtube_video_id

    def get_decrypted_video_id(self):
        """الحصول على Video ID بعد فك التشفير"""
        return self.decrypt_video_id()

    def check_video_access(self, student):
        """تحقق مبسط - يركز فقط على اشتراك الطالب"""
        from enrollments.models import Enrollment
        enrollment = Enrollment.objects.filter(
            student=student,
            course=self.module.course,
            status='active'
        ).first()

        if not enrollment:
            return False, "الطالب غير مسجل في الكورس"

        video_id = self.get_decrypted_video_id()
        if not video_id:
            return False, "لا يوجد فيديو متاح"

        return True, "الفيديو متاح"

    def get_video_url_for_student(self, student):
        """الحصول على رابط الفيديو للطالب"""
        has_access, message = self.check_video_access(student)
        if has_access:
            video_id = self.get_decrypted_video_id()
            if video_id:
                return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1&showinfo=0"
        return None

    def get_previous_lesson(self):
        prev = Lesson.objects.filter(module=self.module, order__lt=self.order).order_by('-order').first()
        if prev:
            return prev
        prev_module = CourseModule.objects.filter(course=self.module.course, order__lt=self.module.order).order_by('-order').first()
        if prev_module:
            return Lesson.objects.filter(module=prev_module).order_by('-order').first()
        return None

    def get_next_lesson(self):
        next_lesson = Lesson.objects.filter(module=self.module, order__gt=self.order).order_by('order').first()
        if next_lesson:
            return next_lesson
        next_module = CourseModule.objects.filter(course=self.module.course, order__gt=self.module.order).order_by('order').first()
        if next_module:
            return Lesson.objects.filter(module=next_module).order_by('order').first()
        return None
    