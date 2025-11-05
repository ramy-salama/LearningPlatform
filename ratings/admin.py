from django.contrib import admin
from .models import CourseRating, TeacherRating

class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['student__name', 'course__title']
    readonly_fields = ['created_at']

class TeacherRatingAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['student__name', 'teacher__name']
    readonly_fields = ['created_at']

admin.site.register(CourseRating, CourseRatingAdmin)
admin.site.register(TeacherRating, TeacherRatingAdmin)