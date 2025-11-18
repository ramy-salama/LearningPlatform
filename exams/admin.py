from django.contrib import admin
from .models import Exam, Choice, Result

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4

class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'teacher', 'start_date', 'end_date', 'is_active']
    list_filter = ['course', 'teacher', 'is_active']

class ResultAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 
        'student_phone',
        'course_title', 
        'teacher_name',
        'score', 
        'percentage', 
        'completed_at'
    ]
    list_filter = ['exam', 'completed_at']
    
    def student_name(self, obj):
        return obj.student.name
    student_name.short_description = 'اسم الطالب'
    
    def student_phone(self, obj):
        return obj.student.phone_number
    student_phone.short_description = 'رقم الهاتف'
    
    def course_title(self, obj):
        return obj.exam.course.title
    course_title.short_description = 'الكورس'
    
    def teacher_name(self, obj):
        return obj.exam.teacher.name
    teacher_name.short_description = 'المعلم'

admin.site.register(Exam, ExamAdmin)
admin.site.register(Result, ResultAdmin)