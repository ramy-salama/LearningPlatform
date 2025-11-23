# admins/views.py - محدث ومكتمل مع إصلاح مشاكل المراسلات
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum, Avg
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.utils import timezone
import json
from datetime import datetime, timedelta
from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from enrollments.models import Enrollment
from messaging.models import Message
from ratings.models import CourseRating
from .models import Admin  # ✅ استيراد نموذج Admin


@staff_member_required
def custom_admin_index(request):
    """صفحة الأدمن الرئيسية مع بيانات التقارير المدمجة"""
    from django.contrib.admin import site

    # جلب الإحصائيات الحية من قاعدة البيانات
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()

    # الإيرادات المالية
    total_revenue = Enrollment.objects.aggregate(total=Sum("amount_paid"))["total"] or 0

    total_purchases = Enrollment.objects.count()
    total_course_students = Enrollment.objects.filter(status="active").count()

    # إيرادات الشهر الحالي
    current_month = datetime.now().month
    monthly_revenue = (
        Enrollment.objects.filter(enrollment_date__month=current_month).aggregate(
            total=Sum("amount_paid")
        )["total"]
        or 0
    )

    # الكورسات الأعلى تقييماً
    top_rated_courses = (
        Course.objects.annotate(avg_rating=Avg("courserating__rating"))
        .filter(avg_rating__isnull=False)
        .order_by("-avg_rating")[:5]
        .values("title", "avg_rating", "teacher__name")
    )

    # الحصول على context الأساسي من الأدمن
    context = site.each_context(request)

    # إضافة بيانات التقارير المدمجة
    context.update(
        {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_courses": total_courses,
            "total_revenue": float(total_revenue),
            "monthly_revenue": float(monthly_revenue),
            "total_purchases": total_purchases,
            "total_course_students": total_course_students,
            "top_rated_courses": list(top_rated_courses),
            "stats_success": True,
        }
    )

    return TemplateResponse(request, "admin/index.html", context)


@csrf_exempt
def get_admin_notifications(request):
    try:
        admin = Admin.objects.first()
        if not admin:
            return JsonResponse({"notifications": []})

        # نحذف الرسائل المقروءة من أكثر من ساعتين فقط
        from django.utils import timezone
        from datetime import timedelta
        
        two_hours_ago = timezone.now() - timedelta(hours=2)
        Message.objects.filter(
            receiver_type="admin",
            receiver_id=admin.id, 
            is_read=True,
            created_at__lt=two_hours_ago
        ).delete()

        # نجيب كل الرسائل (مقروءة وجديدة)
        messages = Message.objects.filter(
            receiver_type="admin", 
            receiver_id=admin.id
            # مش بنحدد is_read علشان نجيب كل حاجة
        ).select_related("sender_student").order_by('-created_at')

        notifications = []
        for msg in messages:
            student_info = "طالب"
            if msg.sender_student:
                student_info = f"{msg.sender_student.name} - {msg.sender_student.phone_number}"

            notifications.append(
                {
                    "icon": "✉️",
                    "title": msg.title,  # ⬅️ عنوان الرسالة اللي كتبها الطالب
                    "student_info": f"{student_info}",  # ⬅️ معلومات الطالب في حقل جديد
                    "preview": msg.content[:150],
                    "time": format_message_time(msg.created_at),
                    "is_read": msg.is_read,  # نرسل الحالة الفعلية
                    "message_id": msg.id,
                }
            )

        return JsonResponse({"notifications": notifications})
    except Exception as e:
        return JsonResponse({"notifications": []})


@csrf_exempt
def mark_message_as_read(request, message_id):
    """تحديد الرسالة كمقروءة"""
    try:
        message = Message.objects.get(id=message_id)
        message.is_read = True
        message.save()
        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'الرسالة غير موجودة'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    



def get_current_admin(request):
    """جلب معرف المسؤول الحالي"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"admin_id": 1})

        admin_user = Admin.objects.filter(email=request.user.email).first()
        return JsonResponse({"admin_id": admin_user.id if admin_user else 1})

    except Exception as e:
        return JsonResponse({"admin_id": 1})


# دالة مساعدة لتنسيق الوقت
def format_message_time(created_at):
    now = timezone.now()
    diff = now - created_at

    if diff.days > 0:
        return f"منذ {diff.days} يوم"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"منذ {hours} ساعة"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"منذ {minutes} دقيقة"
    else:
        return "الآن"
    
    
