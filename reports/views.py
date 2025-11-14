from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from enrollments.models import Enrollment
from ratings.models import CourseRating
import json
from datetime import datetime, timedelta
from django.shortcuts import render

def get_dashboard_stats():
    """دالة مساعدة لجلب إحصائيات الداشبورد"""
    try:
        # الإحصائيات الأساسية
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_courses = Course.objects.count()
        
        # الإيرادات المالية
        total_revenue = Enrollment.objects.aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # إجمالي عمليات الشراء
        total_purchases = Enrollment.objects.count()
        
        # عدد الطلاب في الكورسات
        total_course_students = Enrollment.objects.filter(
            status='active'
        ).count()
        
        # الكورسات الأعلى تقييماً
        top_rated_courses = Course.objects.annotate(
            avg_rating=Avg('courserating__rating')
        ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:5].values(
            'title', 
            'avg_rating',
            'teacher__name'
        )
        
        # إيرادات الشهر الحالي
        current_month = datetime.now().month
        monthly_revenue = Enrollment.objects.filter(
            enrollment_date__month=current_month
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        return {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'total_revenue': float(total_revenue),
            'monthly_revenue': float(monthly_revenue),
            'total_purchases': total_purchases,
            'total_course_students': total_course_students,
            'top_rated_courses': list(top_rated_courses),
            'success': True
        }
    except Exception as e:
        return {
            'total_students': 0,
            'total_teachers': 0,
            'total_courses': 0,
            'total_revenue': 0,
            'monthly_revenue': 0,
            'total_purchases': 0,
            'total_course_students': 0,
            'top_rated_courses': [],
            'success': False,
            'error': str(e)
        }

def financial_report(request):
    """تقرير الإيرادات المالية"""
    try:
        # إحصائيات الإيرادات - استخدام جميع ال enrollments مؤقتاً
        total_revenue = Enrollment.objects.aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        # إيرادات الشهر الحالي
        current_month = datetime.now().month
        monthly_revenue = Enrollment.objects.filter(
            enrollment_date__month=current_month
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # توزيع الإيرادات حسب الكورسات مع اسم المعلم
        course_revenues = Course.objects.annotate(
            total_revenue=Sum('enrollment__amount_paid')
        ).filter(total_revenue__isnull=False).values(
            'title', 
            'total_revenue',
            'teacher__name'
        ).order_by('-total_revenue')[:10]
        
        report_data = {
            'total_revenue': float(total_revenue),
            'monthly_revenue': float(monthly_revenue),
            'course_revenues': list(course_revenues),
            'generated_at': datetime.now().isoformat()
        }
        
        return JsonResponse(report_data)
    except Exception as e:
        return JsonResponse({
            'total_revenue': 0,
            'monthly_revenue': 0,
            'course_revenues': [],
            'error': str(e)
        })

def students_report(request):
    """تقرير إحصائيات الطلاب"""
    try:
        total_students = Student.objects.count()
        
        # طلاب الشهر الحالي - استخدام created_at إذا موجود أو افتراضي
        new_students_this_month = Student.objects.filter(
            created_at__month=datetime.now().month
        ).count() if hasattr(Student, 'created_at') else 0
    
        # توزيع الطلاب حسب المرحلة
        students_by_grade = Student.objects.values('grade').annotate(
            count=Count('id')
        ).order_by('grade')
        
        report_data = {
            'total_students': total_students,
            'new_students_this_month': new_students_this_month,
            'students_by_grade': list(students_by_grade),
            'generated_at': datetime.now().isoformat()
        }
        
        return JsonResponse(report_data)
    except Exception as e:
        return JsonResponse({
            'total_students': 0,
            'new_students_this_month': 0,
            'students_by_grade': [],
            'error': str(e)
        })

def courses_report(request):
    """تقرير إحصائيات الكورسات"""
    try:
        total_courses = Course.objects.count()
        published_courses = Course.objects.count()  # كل الكورسات مؤقتاً
        
        # الكورسات الأعلى تقييماً
        top_rated_courses = Course.objects.annotate(
            avg_rating=Avg('courserating__rating')
        ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10].values(
            'title', 
            'avg_rating',
            'teacher__name'
        )
        
        # الكورسات الأكثر مبيعاً
        best_selling_courses = Course.objects.annotate(
            enrollments_count=Count('enrollment')
        ).order_by('-enrollments_count')[:10].values(
            'title', 
            'enrollments_count',
            'price'
        )
        
        report_data = {
            'total_courses': total_courses,
            'published_courses': published_courses,
            'top_rated_courses': list(top_rated_courses),
            'best_selling_courses': list(best_selling_courses),
            'generated_at': datetime.now().isoformat()
        }
        
        return JsonResponse(report_data)
    except Exception as e:
        return JsonResponse({
            'total_courses': 0,
            'published_courses': 0,
            'top_rated_courses': [],
            'best_selling_courses': [],
            'error': str(e)
        })

def teachers_report(request):
    """تقرير إحصائيات المعلمين"""
    try:
        total_teachers = Teacher.objects.count()
        
        # معلمين الشهر الحالي
        new_teachers_this_month = Teacher.objects.filter(
            created_at__month=datetime.now().month
        ).count()
        
        # توزيع المعلمين حسب المؤهل العلمي
        teachers_by_degree = Teacher.objects.values('degree').annotate(
            count=Count('id')
        ).order_by('degree')
        
        report_data = {
            'total_teachers': total_teachers,
            'new_teachers_this_month': new_teachers_this_month,
            'teachers_by_degree': list(teachers_by_degree),
            'generated_at': datetime.now().isoformat()
        }
        
        return JsonResponse(report_data)
    except Exception as e:
        return JsonResponse({
            'total_teachers': 0,
            'new_teachers_this_month': 0,
            'teachers_by_degree': [],
            'error': str(e)
        })

def dashboard_stats_api(request):
    """API موحد لإحصائيات الداشبورد"""
    stats = get_dashboard_stats()
    return JsonResponse(stats)

def reports_dashboard(request):
    """لوحة تحكم التقارير - مع بيانات ديناميكية"""
    stats = get_dashboard_stats()
    
    # تمرير البيانات للقالب
    context = {
        'total_students': stats['total_students'],
        'total_teachers': stats['total_teachers'],
        'total_courses': stats['total_courses'],
        'total_revenue': stats['total_revenue'],
        'monthly_revenue': stats['monthly_revenue'],
        'total_purchases': stats['total_purchases'],
        'total_course_students': stats['total_course_students'],
        'top_rated_courses': stats['top_rated_courses'],
        'stats_success': stats['success']
    }
    
    return render(request, 'reports/dashboard.html', context)

def financial_report_page(request):
    """تقرير مالي بصفحة ويب"""
    return render(request, 'reports/financial.html')

def students_report_page(request):
    """تقرير الطلاب بصفحة ويب""" 
    return render(request, 'reports/students.html')

def courses_report_page(request):
    """تقرير الكورسات بصفحة ويب"""
    return render(request, 'reports/courses.html')