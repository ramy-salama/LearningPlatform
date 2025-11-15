# admins/admin.py - محدث مع حذف أيقونات المراسلة فقط
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Admin

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'permissions', 'admin_actions']
    list_filter = ['permissions']
    search_fields = ['name', 'email']
    
    def admin_actions(self, obj):
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a class="button" href="/admin/students/student/" title="عرض الطلاب" style="background: #4CAF50; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px;">👥 الطلاب</a>'
            '<a class="button" href="/admin/teachers/teacher/" title="عرض المعلمين" style="background: #2196F3; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px;">👨‍🏫 المعلمين</a>'
            '<a class="button" href="/reports/" title="التقارير التفصيلية" style="background: #FF9800; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px;">📊 التقارير</a>'
            '</div>'
        )
    admin_actions.short_description = 'الإجراءات السريعة'

# تحديث admin.py للطلاب (بدون أيقونات المراسلة)
from students.models import Student
from django.contrib import admin as main_admin

# إلغاء التسجيل القديم إذا كان مسجلاً
try:
    main_admin.site.unregister(Student)
except:
    pass

@main_admin.register(Student)
class StudentAdmin(main_admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'grade', 'year', 'balance']  # ❌ إزالة student_messaging
    search_fields = ['name', 'phone_number']
    list_filter = ['grade', 'year']
    actions = ['delete_selected']
    
    # ❌ تم حذف دالة student_messaging بالكامل
    # ❌ تم حذف الأزرار: ✉️ رسالة و 📨 عرض
    
    def has_add_permission(self, request):
        return False

    # ❌ تم حذف class Media بالكامل (لا حاجة لملفات JavaScript)

# تحديث admin.py للمعلمين (بدون أيقونة المراسلة)
from teachers.models import Teacher

# إلغاء التسجيل القديم إذا كان مسجلاً
try:
    main_admin.site.unregister(Teacher)
except:
    pass

@main_admin.register(Teacher)
class TeacherAdmin(main_admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'status', 'specialization', 'teacher_actions']
    list_filter = ['status', 'specialization', 'teaching_levels']
    search_fields = ['name', 'phone_number', 'email']
    
    def name(self, obj):
        return obj.name
    name.admin_order_field = 'name'
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request):
        return False
    
    def teacher_actions(self, obj):
        return format_html(
            '<div style="display: flex; gap: 5px; flex-wrap: wrap;">'
            '<a class="button" href="{}" style="background: #4CAF50; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; display: inline-flex; align-items: center; gap: 4px;">✅ موافقة</a>'
            '<a class="button" href="{}" style="background: #f44336; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; display: inline-flex; align-items: center; gap: 4px;">❌ رفض</a>'
            # ❌ تم حذف زر: ✉️ مراسلة
            '</div>',
            f'{obj.id}/approve/',
            f'{obj.id}/reject/'
            # ❌ تم حذف: obj.id, f'{obj.id}/change/'
        )
    teacher_actions.short_description = 'الإجراءات'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.approve_teacher),
            path('<path:object_id>/reject/', self.reject_teacher),
        ]
        return custom_urls + urls
    
    def approve_teacher(self, request, object_id):
        teacher = Teacher.objects.get(id=object_id)
        teacher.status = 'approved'
        teacher.save()
        self.message_user(request, f"تم الموافقة على المعلم {teacher.name}")
        return HttpResponseRedirect("../")
    
    def reject_teacher(self, request, object_id):
        teacher = Teacher.objects.get(id=object_id)
        teacher.status = 'rejected'
        teacher.save()
        self.message_user(request, f"تم رفض المعلم {teacher.name}")
        return HttpResponseRedirect("../")