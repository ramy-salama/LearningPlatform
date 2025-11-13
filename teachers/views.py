# teachers/views.py - محدث ومحسن
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

# 🟢 دوال المعلم الأساسية (محفوظة مع تحسينات الأداء)
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

# ===== دوال المراسلة الجديدة (مضافة ومصححة مع تحسينات الأداء) =====

@csrf_exempt
def send_teacher_message(request):
    """إرسال رسالة من المعلم لطلاب الكورس - محسن"""
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'يجب تسجيل الدخول'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            teacher_id = request.session['teacher_id']
            
            # التحقق من البيانات المطلوبة
            if 'course_id' not in data or 'title' not in data or 'content' not in data:
                return JsonResponse({'status': 'error', 'message': 'بيانات غير مكتملة'})

            course_id = data['course_id']

            # التحقق من أن الكورس ملك للمعلم باستخدام select_related
            course = Course.objects.select_related('teacher').only('id', 'teacher_id').get(
                id=course_id, 
                teacher_id=teacher_id
            )
            
            # جلب طلاب الكورس باستعلام فعال
            enrollments = Enrollment.objects.filter(
                course=course
            ).select_related('student').only('student_id')
            
            student_count = enrollments.count()
            
            if student_count == 0:
                return JsonResponse({
                    'status': 'success', 
                    'message': 'لا يوجد طلاب مسجلين في هذا الكورس'
                })

            # إرسال الرسالة لكل طالب
            for enrollment in enrollments:
                Message.objects.create(
                    sender_type='teacher',
                    sender_teacher_id=teacher_id,
                    sender_id=teacher_id,  # للحفاظ على التوافق
                    receiver_type='student',
                    receiver_student_id=enrollment.student.id,
                    receiver_id=enrollment.student.id,  # للحفاظ على التوافق
                    course_id=course_id,
                    title=data['title'],
                    content=data['content']
                )

            return JsonResponse({
                'status': 'success', 
                'message': f'تم إرسال الرسالة إلى {student_count} طالب'
            })

        except Course.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الكورس غير موجود أو ليس ملكك'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'بيانات غير صالحة'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

def get_teacher_notifications(request):
    """الحصول على إشعارات المعلم - محسن"""
    if 'teacher_id' not in request.session:
        return JsonResponse({'messages': []})
    
    try:
        teacher_id = request.session['teacher_id']
        
        # تحسين الاستعلام باستخدام select_related
        messages = Message.objects.filter(
            receiver_type='teacher',
            receiver_id=teacher_id
        ).select_related(
            'sender_admin',
            'sender_student',
            'sender_teacher'
        ).only(
            'id',
            'title',
            'content',
            'is_read',
            'created_at',
            'sender_type'
        ).order_by('-created_at')[:10]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name()
            })

        return JsonResponse({'messages': message_list})
    
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

def get_teacher_courses(request):
    """الحصول على كورسات المعلم للمراسلة - محسن"""
    if 'teacher_id' not in request.session:
        return JsonResponse({'courses': []})
    
    try:
        teacher_id = request.session['teacher_id']
        
        # استعلام فعال مع annotation لعدد الطلاب
        courses = Course.objects.filter(
            teacher_id=teacher_id, 
            status='published'
        ).annotate(
            enrolled_students=Count('enrollment')
        ).only(
            'id', 
            'title'
        ).order_by('title')

        course_list = []
        for course in courses:
            course_list.append({
                'id': course.id,
                'title': course.title,
                'students_count': course.enrolled_students
            })

        return JsonResponse({'courses': course_list})
    
    except Exception as e:
        return JsonResponse({'courses': [], 'error': str(e)})

# دوال جديدة للمعلم - محسنة
def get_teacher_unread_count(request):
    """عدد الرسائل غير المقروءة للمعلم - محسن"""
    if 'teacher_id' not in request.session:
        return JsonResponse({'unread_count': 0})
    
    try:
        teacher_id = request.session['teacher_id']
        
        count = Message.objects.filter(
            receiver_type='teacher',
            receiver_id=teacher_id,
            is_read=False
        ).count()
        
        return JsonResponse({'unread_count': count})
    
    except Exception as e:
        return JsonResponse({'unread_count': 0, 'error': str(e)})

@csrf_exempt
def mark_teacher_message_read(request, message_id):
    """وضع علامة مقروء على رسالة المعلم - محسن"""
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'يجب تسجيل الدخول'})
    
    try:
        teacher_id = request.session['teacher_id']
        
        message = Message.objects.filter(
            id=message_id, 
            receiver_type='teacher', 
            receiver_id=teacher_id
        ).first()
        
        if not message:
            return JsonResponse({'status': 'error', 'message': 'الرسالة غير موجودة'})
        
        message.mark_as_read()
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})