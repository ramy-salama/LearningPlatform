from django.db import models
from students.models import Student
from courses.models import Course


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('active', 'نشط'), 
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('paid', 'مدفوع'),
        ('failed', 'فاشل'),
        ('refunded', 'تم الاسترداد'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="الكورس")
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الحجز")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الحجز")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="حالة الدفع")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ المدفوع")
    progress = models.IntegerField(default=0, verbose_name="نسبة الإكمال")
    last_accessed = models.DateTimeField(auto_now=True, verbose_name="آخر دخول")
    
    # إضف هذا الحقل الجديد
    completed_lessons = models.JSONField(default=list, verbose_name="الدروس المكتملة")  # بيخزن [1, 2, 3] أي دي الدروس
    
    def update_progress(self):
        """تحديث التقدم بناءً على الدروس المكتملة"""
        # حساب إجمالي الدروس من خلال الـ modules
        total_lessons = 0
        for module in self.course.modules.all():
            total_lessons += module.lessons.count()
        
        if total_lessons > 0:
            completed_count = len(self.completed_lessons)
            self.progress = (completed_count / total_lessons) * 100
        else:
            self.progress = 0
        
        self.save()
        return self.progress

    def mark_lesson_completed(self, lesson_id):
        """وضع علامة على درس كمكتمل"""
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)
            self.update_progress()  # حدث التقدم تلقائياً

    def get_completed_count(self):
        """عدد الدروس المكتملة"""
        return len(self.completed_lessons)

    def get_total_lessons(self):
        """إجمالي الدروس في الكورس"""
        total_lessons = 0
        for module in self.course.modules.all():
            total_lessons += module.lessons.count()
        return total_lessons

    class Meta:
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.name} - {self.course.title}"
class TopUpRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ المطلوب شحنه")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الطلب")
    proof_of_payment = models.CharField(max_length=255, blank=True, verbose_name="رابط إثبات الدفع (WhatsApp)")
    
    class Meta:
        verbose_name = 'طلب شحن رصيد'
        verbose_name_plural = 'طلبات شحن الرصيد'

    def __str__(self):
        return f"طلب شحن لـ {self.student.name} بمبلغ {self.amount}"