from django.db import models
from courses.models import Course
from teachers.models import Teacher
from students.models import Student
from django.utils import timezone




class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    duration = models.IntegerField(help_text="المدة بالدقائق (30-180)")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    points_per_question = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)  # اجعله True افتراضياً
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def status(self):
        """حالة الاختبار تلقائياً بناءً على الوقت والأسئلة"""
        now = timezone.now()
        question_count = self.question_set.count()
        
        if question_count < 10:
            return "غير مكتمل"
        elif self.start_date > now:
            return "قيد الانتظار"
        elif self.end_date < now:
            return "منتهي"
        elif self.start_date <= now <= self.end_date:
            return "نشط"
        else:
            return "غير نشط"




class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='exam_questions/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"سؤال {self.order} - {self.exam.title}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict)  # للمعلم فقط

    def __str__(self):
        return f"{self.student.name} - {self.exam.title}"

    class Meta:
        unique_together = ['exam', 'student']


        