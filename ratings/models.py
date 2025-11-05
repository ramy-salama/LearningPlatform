from django.db import models
from courses.models import Course
from students.models import Student
from teachers.models import Teacher

class CourseRating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="الكورس")
    rating = models.IntegerField(verbose_name="التقييم", choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, verbose_name="المراجعة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقييم")
    
    class Meta:
        verbose_name = 'تقييم كورس'
        verbose_name_plural = 'تقييمات الكورسات'
        unique_together = ['student', 'course']  # منع التقييم المزدوج

class TeacherRating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="المعلم")
    rating = models.IntegerField(verbose_name="التقييم", choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, verbose_name="المراجعة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقييم")
    
    class Meta:
        verbose_name = 'تقييم معلم'
        verbose_name_plural = 'تقييمات المعلمين'