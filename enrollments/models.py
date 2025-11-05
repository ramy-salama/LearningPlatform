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
    
    class Meta:
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.name} - {self.course.title}"