from django.contrib import admin
from .models import Report

class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'period_start', 'period_end', 'generated_at']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title']
    readonly_fields = ['generated_at']
    
    fieldsets = (
        ('معلومات التقرير', {
            'fields': ('report_type', 'title', 'period_start', 'period_end')
        }),
        ('بيانات التقرير', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Report, ReportAdmin)