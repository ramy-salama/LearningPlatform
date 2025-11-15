from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'grade', 'year', 'balance']
    # تم إزالة عمود المراسلة تماماً

admin.site.register(Student, StudentAdmin)