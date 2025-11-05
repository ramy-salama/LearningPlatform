from django.db import models
from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from enrollments.models import Enrollment

class Report(models.Model):
    REPORT_TYPES = [
        ('financial', 'تقرير مالي'),
        ('students', 'تقرير الطلاب'),
        ('teachers', 'تقرير المعلمين'),
        ('courses', 'تقرير الكورسات'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="نوع التقرير")
    title = models.CharField(max_length=200, verbose_name="عنوان التقرير")
    data = models.JSONField(verbose_name="بيانات التقرير")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")
    period_start = models.DateField(verbose_name="بداية الفترة")
    period_end = models.DateField(verbose_name="نهاية الفترة")
    
    class Meta:
        verbose_name = 'تقرير'
        verbose_name_plural = 'التقارير'

    def __str__(self):
        return f"{self.title} - {self.generated_at}"