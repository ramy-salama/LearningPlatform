from django.contrib import admin
from .models import Enrollment

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_date', 'status', 'payment_status', 'amount_paid', 'progress']
    list_filter = ['status', 'payment_status', 'enrollment_date']
    search_fields = ['student__name', 'course__title']
    readonly_fields = ['enrollment_date', 'last_accessed']
    
    fieldsets = (
        ('معلومات الحجز', {
            'fields': ('student', 'course', 'enrollment_date', 'last_accessed')
        }),
        ('حالة الحجز', {
            'fields': ('status', 'progress')
        }),
        ('المعلومات المالية', {
            'fields': ('payment_status', 'amount_paid')
        }),
    )

admin.site.register(Enrollment, EnrollmentAdmin)