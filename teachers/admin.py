# teachers/admin.py - محدث ومحسن
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import path
from django.db.models import Count
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'phone_number', 
        'email', 
        'specialization', 
        'teaching_levels_display',
        'status_badge',
        'approval_actions'
    ]
    
    list_filter = [
        'status', 
        'specialization', 
        'teaching_levels',
        'degree',
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'phone_number', 
        'email',
        'specialization'
    ]
    
    readonly_fields = [
        'created_at',
        'teacher_info_card',
        'approval_history'
    ]
    
    fieldsets = (
        ('المعلومات الشخصية', {
            'fields': (
                'name',
                'phone_number', 
                'email',
                'address',
                'profile_image',
                'certificate_image'
            )
        }),
        ('المعلومات الأكاديمية', {
            'fields': (
                'specialization',
                'teaching_levels',
                'degree',
                'major',
                'experience',
                'certificates'
            )
        }),
        ('المعلومات المالية', {
            'fields': (
                'profit_percentage',
                'payment_method',
                'account_number'
            )
        }),
        ('حالة الطلب', {
            'fields': (
                'status',
                'teacher_info_card',
                'approval_history'
            )
        }),
        ('السيرة الذاتية', {
            'fields': ('bio',),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'approve_selected_teachers',
        'reject_selected_teachers',
        'send_bulk_message_to_approved'
    ]
    
    def teaching_levels_display(self, obj):
        """عرض المراحل التعليمية بشكل منسق"""
        levels = obj.teaching_levels.split(',') if obj.teaching_levels else []
        level_names = {
            'primary': 'ابتدائي',
            'preparatory': 'إعدادي', 
            'secondary': 'ثانوي'
        }
        display_levels = [level_names.get(level, level) for level in levels]
        return ', '.join(display_levels) if display_levels else '---'
    teaching_levels_display.short_description = 'المراحل'
    
    def status_badge(self, obj):
        """عرض حالة المعلم بشارة ملونة"""
        status_config = {
            'pending': ('🔵 قيد الانتظار', '#3498db'),
            'approved': ('✅ مقبول', '#27ae60'), 
            'rejected': ('❌ مرفوض', '#e74c3c')
        }
        
        text, color = status_config.get(obj.status, ('⚪ غير معروف', '#95a5a6'))
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, text
        )
    status_badge.short_description = 'الحالة'
    
    def approval_actions(self, obj):
        """أزرار الإجراءات السريعة مع خيارات المراسلة"""
        base_actions = format_html(
            '<div style="display: flex; gap: 5px; flex-wrap: wrap; min-width: 200px;">'
            '<a class="button" href="{}" style="background: #27ae60; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">✅ موافقة</a>'
            '<a class="button" href="{}" style="background: #e74c3c; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">❌ رفض</a>',
            f'{obj.id}/approve/',
            f'{obj.id}/reject/'
        )
        
        # إضافة زر المراسلة للمعلمين المقبولين
        if obj.status == 'approved':
            messaging_action = format_html(
                '<button onclick="sendMessageToTeacher({})" style="background: #3498db; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">✉️ مراسلة</button>',
                obj.id
            )
            base_actions += messaging_action
        
        base_actions += format_html(
            '<a class="button" href="{}" style="background: #95a5a6; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">👀 عرض</a>'
            '</div>',
            f'{obj.id}/change/'
        )
        
        return base_actions
    approval_actions.short_description = 'الإجراءات'
    
    def teacher_info_card(self, obj):
        """بطاقة معلومات سريعة عن المعلم"""
        if not obj.pk:
            return "---"
            
        levels = obj.teaching_levels.split(',') if obj.teaching_levels else []
        level_names = {
            'primary': 'ابتدائي',
            'preparatory': 'إعدادي',
            'secondary': 'ثانوي'
        }
        display_levels = [level_names.get(level, level) for level in levels]
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; margin: 10px 0;">'
            '<h4 style="margin: 0 0 10px 0; color: #2c3e50;">📋 معلومات المعلم</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">'
            '<div><strong>التخصص:</strong> {}</div>'
            '<div><strong>المؤهل:</strong> {}</div>'
            '<div><strong>المراحل:</strong> {}</div>'
            '<div><strong>نسبة الأرباح:</strong> {}%</div>'
            '<div><strong>طريقة الدفع:</strong> {}</div>'
            '<div><strong>رقم الحساب:</strong> {}</div>'
            '</div>'
            '</div>',
            obj.specialization,
            obj.get_degree_display(),
            ', '.join(display_levels) if display_levels else '---',
            obj.profit_percentage,
            obj.get_payment_method_display(),
            obj.account_number
        )
    teacher_info_card.short_description = 'معلومات سريعة'
    
    def approval_history(self, obj):
        """سجل الموافقة على المعلم"""
        status_history = {
            'pending': 'تم تقديم الطلب في {}',
            'approved': 'تمت الموافقة على الطلب في {}',
            'rejected': 'تم رفض الطلب في {}'
        }
        
        history_text = status_history.get(obj.status, 'حالة غير معروفة').format(
            obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else '---'
        )
        
        return format_html(
            '<div style="background: #fff3cd; padding: 10px; border-radius: 6px; border: 1px solid #ffeaa7; margin: 10px 0;">'
            '<strong>📝 سجل الحالة:</strong> {}'
            '</div>',
            history_text
        )
    approval_history.short_description = 'سجل الموافقة'
    
    # الإجراءات الجماعية
    def approve_selected_teachers(self, request, queryset):
        """موافقة جماعية على المعلمين المحددين"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'تمت الموافقة على {updated} معلم')
    approve_selected_teachers.short_description = '✅ الموافقة على المعلمين المحددين'
    
    def reject_selected_teachers(self, request, queryset):
        """رفض جماعي للمعلمين المحددين"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'تم رفض {updated} معلم')
    reject_selected_teachers.short_description = '❌ رفض المعلمين المحددين'
    
    def send_bulk_message_to_approved(self, request, queryset):
        """إرسال رسالة جماعية للمعلمين المقبولين"""
        approved_teachers = queryset.filter(status='approved')
        
        if not approved_teachers:
            self.message_user(request, 'لا توجد معلمين مقبولين في التحديد', level='ERROR')
            return
        
        # حفظ معرفات المعلمين في الجلسة لاستخدامها في المراسلة
        teacher_ids = list(approved_teachers.values_list('id', flat=True))
        request.session['bulk_teacher_ids'] = teacher_ids
        
        self.message_user(
            request, 
            f'تم تحضير {len(teacher_ids)} معلم للمراسلة الجماعية. '
            'استخدم أيقونة المراسلة الجماعية في الهيدر.'
        )
    send_bulk_message_to_approved.short_description = '📢 إرسال رسالة جماعية للمعلمين المقبولين'
    
    # URLs المخصصة
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.approve_teacher),
            path('<path:object_id>/reject/', self.reject_teacher),
            path('bulk-messaging/', self.bulk_messaging_view, name='teachers_bulk_messaging'),
        ]
        return custom_urls + urls
    
    def approve_teacher(self, request, object_id):
        """موافقة على معلم فردي"""
        teacher = Teacher.objects.get(id=object_id)
        teacher.status = 'approved'
        teacher.save()
        self.message_user(request, f"تم الموافقة على المعلم {teacher.name}")
        return HttpResponseRedirect("../")
    
    def reject_teacher(self, request, object_id):
        """رفض معلم فردي"""
        teacher = Teacher.objects.get(id=object_id)
        teacher.status = 'rejected'
        teacher.save()
        self.message_user(request, f"تم رفض المعلم {teacher.name}")
        return HttpResponseRedirect("../")
    
    def bulk_messaging_view(self, request):
        """عرض واجهة المراسلة الجماعية"""
        from django.shortcuts import render
        teacher_ids = request.session.get('bulk_teacher_ids', [])
        teachers = Teacher.objects.filter(id__in=teacher_ids, status='approved')
        
        context = {
            'teachers': teachers,
            'teacher_count': teachers.count()
        }
        
        return render(request, 'admin/teachers_bulk_messaging.html', context)
    
    # تحسينات الأداء
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    # أذونات
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    class Media:
        css = {
            'all': ('admin/css/teacher_admin.css',)
        }
        js = ('admin/js/teacher_admin.js',)

# إضافة إحصائيات سريعة في صفحة المعلمين
class TeacherStatsAdmin(admin.ModelAdmin):
    """إحصائيات سريعة عن المعلمين"""
    
    def changelist_view(self, request, extra_context=None):
        # إحصائيات سريعة
        stats = {
            'total_teachers': Teacher.objects.count(),
            'approved_teachers': Teacher.objects.filter(status='approved').count(),
            'pending_teachers': Teacher.objects.filter(status='pending').count(),
            'rejected_teachers': Teacher.objects.filter(status='rejected').count(),
        }
        
        extra_context = extra_context or {}
        extra_context['stats'] = stats
        
        return super().changelist_view(request, extra_context=extra_context)