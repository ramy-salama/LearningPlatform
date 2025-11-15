# teachers/views.py - محدث ومحسن (بدون نظام المراسلة)
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Avg, Sum, Count
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Teacher
from courses.models import Course
from enrollments.models import Enrollment
from messaging.models import Message
from decimal import Decimal

# 🟢 دوال المعلم الأساسية (محفوظة بالكامل)
def teacher_register(request):
    # الكود الأصلي محفوظ بالكامل مع تحسينات طفيفة
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            password = request.POST.get('password')
            address = request.POST.get('address')
            bio = request.POST.get('bio')
            specialization = request.POST.get('specialization')
            experience = request.POST.get('experience')
            teaching_levels = request.POST.getlist('teaching_levels')
            degree = request.POST.get('degree')
            major = request.POST.get('major')
            certificates = request.POST.get('certificates', '')
            profile_image = request.FILES.get('profile_image')
            certificate_image = request.FILES.get('certificate_image')
            payment_method = request.POST.get('payment_method')
            account_number = request.POST.get('account_number', '')
            profit_percentage = request.POST.get('profit_percentage', 50)

            teacher = Teacher(
                name=name,
                phone_number=phone_number,
                email=email,
                password=password,  # سيتم تشفيرها تلقائياً في save()
                address=address,
                bio=bio,
                specialization=specialization,
                teaching_levels=','.join(teaching_levels),
                experience=experience,
                degree=degree,
                major=major,
                certificates=certificates,
                payment_method=payment_method,
                account_number=account_number,
                profit_percentage=profit_percentage,
                status='pending'
            )

            if profile_image:
                teacher.profile_image = profile_image
            if certificate_image:
                teacher.certificate_image = certificate_image

            teacher.save()
            return render(request, 'teachers/register_success.html')

        except Exception as e:
            return render(request, 'teachers/register.html', {'error': f'حدث خطأ: {str(e)}'})

    return render(request, 'teachers/register.html')

def teacher_login(request):
    # الكود الأصلي محفوظ بالكامل مع تحسينات الأمان
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        try:
            teacher = Teacher.objects.get(phone_number=phone_number)
            
            # استخدام check_password للتحقق الآمن
            if teacher.check_password(password):
                if teacher.status == 'approved':
                    request.session['teacher_id'] = teacher.id
                    request.session['teacher_name'] = teacher.name
                    return redirect('/teachers/dashboard/')
                elif teacher.status == 'pending':
                    return render(request, 'teachers/login.html', {'error': 'لم تتم الموافقة على حسابك بعد'})
                elif teacher.status == 'rejected':
                    return render(request, 'teachers/login.html', {'error': 'تم رفض طلب التسجيل الخاص بك'})
            else:
                return render(request, 'teachers/login.html', {'error': 'رقم الهاتف أو كلمة المرور غير صحيحة'})

        except Teacher.DoesNotExist:
            return render(request, 'teachers/login.html', {'error': 'رقم الهاتف أو كلمة المرور غير صحيحة'})
        except Exception as e:
            return render(request, 'teachers/login.html', {'error': f'حدث خطأ أثناء تسجيل الدخول: {str(e)}'})

    return render(request, 'teachers/login.html')

def teacher_dashboard(request):
    if 'teacher_id' not in request.session:
        return redirect('teacher_login')

    try:
        teacher = Teacher.objects.only(
            'id', 'name', 'profile_image', 'specialization', 
            'email', 'profit_percentage', 'payment_method', 'account_number'
        ).get(id=request.session['teacher_id'])
        
        # تحسين استعلامات الإحصائيات باستخدام aggregation
        courses_stats = Course.objects.filter(
            teacher=teacher
        ).aggregate(
            total_courses=Count('id'),
            average_rating=Avg('average_rating'),
            total_students=Sum('students_count')
        )
        
        # حساب الإيرادات باستخدام استعلام فعال
        earnings_data = Enrollment.objects.filter(
            course__teacher=teacher
        ).aggregate(
            total_earnings=Sum('amount_paid')
        )
        
        total_earnings = earnings_data['total_earnings'] or 0
        if total_earnings:
            total_earnings = total_earnings * (Decimal(teacher.profit_percentage) / Decimal(100))

        context = {
            'teacher': teacher,
            'total_courses': courses_stats['total_courses'] or 0,
            'total_students': courses_stats['total_students'] or 0,
            'average_rating': round(courses_stats['average_rating'] or 0, 2),
            'total_earnings': round(total_earnings, 2),
        }

        return render(request, 'teachers/dashboard.html', context)

    except Teacher.DoesNotExist:
        request.session.flush()
        return redirect('teacher_login')
    except Exception as e:
        return render(request, 'teachers/error.html', {
            'error': f'حدث خطأ في تحميل البيانات: {str(e)}'
        })

def teacher_profile(request, teacher_id):
    # الكود الأصلي محفوظ مع تحسينات الاستعلام
    teacher = get_object_or_404(
        Teacher.objects.select_related().only(
            'name', 'profile_image', 'specialization', 'bio',
            'experience', 'degree', 'major', 'certificates'
        ), 
        id=teacher_id
    )
    
    teacher_courses = Course.objects.filter(
        teacher=teacher, 
        status='published'
    ).only(
        'id', 'title', 'image', 'price', 'students_count', 'average_rating'
    ).order_by('-created_at')[:12]  # تحديد عدد الكورسات المعروضة

    return render(request, 'teachers/teacher_profile.html', {
        'teacher': teacher,
        'courses': teacher_courses
    })

def teacher_logout(request):
    if 'teacher_id' in request.session:
        del request.session['teacher_id']
    if 'teacher_name' in request.session:
        del request.session['teacher_name']
    return redirect('/teachers/login/')