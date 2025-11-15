# messaging/models.py - مضاد للأخطاء مع البيانات القديمة (بدون علاقات المعلم)
from django.db import models
from django.utils import timezone
from datetime import timedelta
from students.models import Student
from admins.models import Admin  # ✅ إزالة استيراد Teacher

class Message(models.Model):
    SENDER_TYPES = [
        ('admin', 'الإدارة'),
        ('student', 'طالب'),
        # ✅ إزالة 'teacher' من الخيارات
    ]
    
    RECEIVER_TYPES = [
        ('admin', 'الإدارة'),
        ('student', 'طالب'),
        ('all_students', 'كل الطلاب'),
        ('course_students', 'طلاب كورس محدد'),
        # ✅ إزالة 'teacher' من الخيارات
    ]
    
    # العلاقات الحقيقية مع المستخدمين (بدون المعلم)
    sender_admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_messages_admin')
    sender_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_messages_student')
    
    receiver_admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages_admin')
    receiver_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages_student')
    
    # الحقول الأساسية (للتوافق مع البيانات القديمة)
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPES)
    sender_id = models.BigIntegerField()
    receiver_type = models.CharField(max_length=20, choices=RECEIVER_TYPES)
    receiver_id = models.BigIntegerField(null=True, blank=True)
    course_id = models.BigIntegerField(null=True, blank=True)
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    is_reply = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        
        # تعيين العلاقات الحقيقية بناءً على sender_type و receiver_type (بدون المعلم)
        if self.sender_type == 'admin' and self.sender_id:
            try:
                self.sender_admin = Admin.objects.get(id=self.sender_id)
            except Admin.DoesNotExist:
                pass
        elif self.sender_type == 'student' and self.sender_id:
            try:
                self.sender_student = Student.objects.get(id=self.sender_id)
            except Student.DoesNotExist:
                pass
        
        if self.receiver_type == 'admin' and self.receiver_id:
            try:
                self.receiver_admin = Admin.objects.get(id=self.receiver_id)
            except Admin.DoesNotExist:
                pass
        elif self.receiver_type == 'student' and self.receiver_id:
            try:
                self.receiver_student = Student.objects.get(id=self.receiver_id)
            except Student.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def get_sender_name(self):
        """الحصول على اسم المرسل - مع العلاقات الحقيقية (بدون المعلم)"""
        try:
            if self.sender_admin:
                return self.sender_admin.name
            elif self.sender_student:
                return self.sender_student.name
            elif self.sender_type == 'admin':
                return "الإدارة"
            elif self.sender_type == 'student':
                return "طالب"
        except Exception:
            pass
        return "مرسل"
    
    def get_receiver_name(self):
        """الحصول على اسم المستقبل - مع العلاقات الحقيقية (بدون المعلم)"""
        try:
            if self.receiver_admin:
                return self.receiver_admin.name
            elif self.receiver_student:
                return self.receiver_student.name
            elif self.receiver_type == 'admin':
                return "الإدارة"
            elif self.receiver_type == 'student':
                return "طالب"
            elif self.receiver_type == 'all_students':
                return "كل الطلاب"
            elif self.receiver_type == 'course_students':
                return "طلاب الكورس"
        except Exception:
            pass
        return "مستقبل"
    
    def is_expired(self):
        """التحقق إذا انتهت صلاحية الرسالة"""
        return timezone.now() > self.expires_at
    
    def can_reply(self):
        """التحقق إذا كان يمكن الرد على الرسالة"""
        return not self.is_reply and not self.is_expired()
    
    class Meta:
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'
        ordering = ['-created_at']

class Notification(models.Model):
    user_type = models.CharField(max_length=20)
    user_id = models.BigIntegerField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_user_name(self):
        """الحصول على اسم المستخدم"""
        return "مستخدم"
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']