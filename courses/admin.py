from django.contrib import admin
from .models import Course, CourseModule, Lesson

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    show_change_link = True
    inlines = [LessonInline]

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'category', 'price', 'status', 'students_count', 'average_rating']
    list_filter = ['status', 'category', 'language', 'teacher']
    search_fields = ['title', 'description', 'category']
    inlines = [CourseModuleInline]
    
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('teacher', 'title', 'description', 'category', 'price', 'image', 'language')
        }),
        ('إعدادات الكورس', {
            'fields': ('status', 'start_date', 'end_date', 'estimated_duration', 'prerequisites')
        }),
        ('النظام المالي', {
            'fields': ('teacher_percentage',)
        }),
        ('الإحصائيات', {
            'fields': ('students_count', 'average_rating'),
            'classes': ('collapse',)
        }),
    )

class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [LessonInline]

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'youtube_video_id', 'order', 'duration']  # أضفت youtube_video_id
    list_filter = ['lesson_type', 'module__course']
    search_fields = ['title', 'content']

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseModule, CourseModuleAdmin)
admin.site.register(Lesson, LessonAdmin)