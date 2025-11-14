# students/views.py - محدث ومصحح
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
import json
from .models import Student
from enrollments.models import Enrollment
from messaging.models import Message
from courses.models import Course
from decimal import Decimal, InvalidOperation

# ===============================
# دوال الطالب الأساسية (محفوظة بالكامل مع تحسينات الأداء)
# ===============================

def student_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        parent_phone = request.POST.get('parent_phone')
        password = request.POST.get('password')
        residence = request.POST.get('residence')
        grade = request.POST.get('grade')
        year = request.POST.get('year')
        
        # ✅ معالجة رفع الصورة الشخصية
        profile_image = request.FILES.get('profile_image')

        if not all([name, phone_number, parent_phone, password, residence, grade, year]):
            return render(request, 'students/register.html', {
                'error': 'جميع الحقول مطلوبة'
            })

        if Student.objects.filter(phone_number=phone_number).exists():
            return render(request, 'students/register.html', {
                'error': 'رقم الهاتف مسجل مسبقاً! الرجاء استخدام رقم آخر أو تسجيل الدخول'
            })

        try:
            student = Student(
                name=name,
                phone_number=phone_number,
                parent_phone=parent_phone,
                password=password,  # سيتم تشفيرها تلقائياً في save()
                residence=residence,
                grade=grade,
                year=year,
                profile_image=profile_image  # ✅ إضافة الصورة الشخصية
            )
            student.save()
            return redirect('students:student_login')

        except IntegrityError:
            return render(request, 'students/register.html', {
                'error': 'رقم الهاتف مسجل مسبقاً! الرجاء استخدام رقم آخر'
            })
        except Exception as e:
            return render(request, 'students/register.html', {
                'error': f'حدث خطأ أثناء التسجيل: {str(e)}'
            })

    return render(request, 'students/register.html')

def student_login(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        if not phone_number or not password:
            return render(request, 'students/login.html', {
                'error': 'رقم الهاتف وكلمة المرور مطلوبان'
            })

        try:
            # استخدام select_related إذا كان هناك علاقات (للتوافق المستقبلي)
            student = Student.objects.get(phone_number=phone_number)
            
            # استخدام check_password للتحقق الآمن
            if student.check_password(password):
                request.session['student_id'] = student.id
                request.session['student_name'] = student.name
                return redirect('students:student_dashboard')
            else:
                return render(request, 'students/login.html', {
                    'error': 'رقم الهاتف أو كلمة المرور غير صحيحة'
                })

        except Student.DoesNotExist:
            return render(request, 'students/login.html', {
                'error': 'رقم الهاتف أو كلمة المرور غير صحيحة'
            })
        except Exception as e:
            return render(request, 'students/login.html', {
                'error': f'حدث خطأ أثناء تسجيل الدخول: {str(e)}'
            })

    return render(request, 'students/login.html')

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('students:student_login')

    try:
        # تحسين الاستعلام باستخدام select_related
        student = Student.objects.get(id=request.session['student_id'])
        
        # تحسين استعلامات الاشتراكات
        enrollments = Enrollment.objects.filter(
            student=student,
            status__in=['active', 'completed']
        ).select_related(
            'course', 
            'course__teacher'
        ).only(
            'course__title',
            'course__teacher__name',
            'amount_paid',
            'enrollment_date',
            'status',
            'progress'
        ).order_by('-enrollment_date')

        return render(request, 'students/dashboard.html', {
            'student': student,
            'enrollments': enrollments
        })

    except Student.DoesNotExist:
        request.session.flush()
        return redirect('students:student_login')
    except Exception as e:
        return render(request, 'students/error.html', {
            'error': f'حدث خطأ في تحميل البيانات: {str(e)}'
        })

def wallet_topup(request):
    if 'student_id' not in request.session:
        return redirect('students:student_login')

    try:
        student = Student.objects.get(id=request.session['student_id'])

        if request.method == 'POST':
            amount = request.POST.get('amount')

            if not amount:
                return render(request, 'students/wallet_topup.html', {
                    'student': student,
                    'error': 'يرجى إدخال المبلغ'
                })

            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    return render(request, 'students/wallet_topup.html', {
                        'student': student,
                        'error': 'المبلغ يجب أن يكون أكبر من الصفر'
                    })

                student.balance += amount_decimal
                student.save()
                return redirect('students:student_dashboard')

            except InvalidOperation:
                return render(request, 'students/wallet_topup.html', {
                    'student': student,
                    'error': 'المبلغ غير صحيح'
                })
            except Exception as e:
                return render(request, 'students/wallet_topup.html', {
                    'student': student,
                    'error': f'حدث خطأ أثناء شحن الرصيد: {str(e)}'
                })

        return render(request, 'students/wallet_topup.html', {'student': student})

    except Student.DoesNotExist:
        request.session.flush()
        return redirect('students:student_login')
    except Exception as e:
        return render(request, 'students/error.html', {
            'error': f'حدث خطأ: {str(e)}'
        })

def wallet_balance(request):
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'يجب تسجيل الدخول'}, status=401)

    try:
        student = Student.objects.only('balance', 'bonus_balance', 'total_spent').get(
            id=request.session['student_id']
        )
        return JsonResponse({
            'balance': float(student.balance),
            'bonus_balance': float(student.bonus_balance),
            'total_spent': float(student.total_spent)
        })

    except Student.DoesNotExist:
        return JsonResponse({'error': 'الطالب غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'حدث خطأ: {str(e)}'}, status=500)

def student_logout(request):
    request.session.flush()
    return redirect('students:student_login')

# ===============================
# دوال المراسلة الجديدة (مصححة بالكامل)
# ===============================

def get_student_notifications(request):
    """الحصول على إشعارات الطالب - محسن"""
    if 'student_id' not in request.session:
        return JsonResponse({'messages': []})

    try:
        student_id = request.session['student_id']
        
        # تحسين الاستعلام باستخدام select_related
        messages = Message.objects.filter(
            receiver_type='student',
            receiver_id=student_id
        ).select_related(
            'sender_admin',
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
                'sender_name': msg.get_sender_name(),
                'has_replies': hasattr(msg, 'replies') and msg.replies.exists()
            })

        return JsonResponse({'messages': message_list})

    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

@csrf_exempt
def send_student_message(request):
    """إرسال رسالة من الطالب إلى الإدارة - مصحح"""
    if 'student_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'يجب تسجيل الدخول'})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = request.session['student_id']
            
            # التحقق من وجود الطالب
            student = Student.objects.only('id').get(id=student_id)

            # التحقق من البيانات المطلوبة
            if 'title' not in data or 'content' not in data:
                return JsonResponse({'status': 'error', 'message': 'العنوان والمحتوى مطلوبان'})

            # ✅ إصلاح المشكلة: استخدام الحقول الصحيحة لنموذج Message
            message = Message.objects.create(
                sender_type='student',
                sender_id=student_id,  # ✅ استخدام sender_id بدلاً من sender_student_id
                receiver_type='admin',
                title=data['title'],
                content=data['content']
            )
            return JsonResponse({'status': 'success', 'message_id': message.id})

        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الطالب غير موجود'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'بيانات غير صالحة'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'حدث خطأ: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

def get_student_conversation(request, message_id):
    """جلب محادثة كاملة للطالب - مصحح"""
    if 'student_id' not in request.session:
        return JsonResponse({'conversation': []})

    try:
        student_id = request.session['student_id']
        
        # تحسين الاستعلام مع prefetch_related للردود
        main_message = Message.objects.filter(
            id=message_id, 
            receiver_type='student', 
            receiver_id=student_id
        ).first()
        
        if not main_message:
            return JsonResponse({'conversation': []})
        
        conversation = []
        
        # إضافة الرسالة الرئيسية
        conversation.append({
            'id': main_message.id,
            'title': main_message.title,
            'content': main_message.content,
            'is_read': main_message.is_read,
            'created_at': main_message.created_at.strftime('%Y-%m-%d %H:%M'),
            'sender_type': main_message.sender_type,
            'sender_name': main_message.get_sender_name(),
            'is_main': True
        })
        
        # إضافة الردود إذا كان هناك علاقة replies
        if hasattr(main_message, 'replies'):
            replies = main_message.replies.all().order_by('created_at')
            for reply in replies:
                conversation.append({
                    'id': reply.id,
                    'content': reply.content,
                    'is_read': reply.is_read,
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M'),
                    'sender_type': reply.sender_type,
                    'sender_name': reply.get_sender_name(),
                    'is_main': False
                })
        
        return JsonResponse({'conversation': conversation})
    
    except Message.DoesNotExist:
        return JsonResponse({'conversation': []})
    except Exception as e:
        return JsonResponse({'conversation': [], 'error': str(e)})

def get_unread_student_messages(request):
    """جلب الرسائل غير المقروءة للطالب - مصحح"""
    if 'student_id' not in request.session:
        return JsonResponse({'messages': []})

    try:
        student_id = request.session['student_id']
        
        # استعلام محسن مع select_related
        messages = Message.objects.filter(
            receiver_type='student',
            receiver_id=student_id,
            is_read=False
        ).select_related(
            'sender_admin',
            'sender_teacher'
        ).only(
            'id',
            'title', 
            'content',
            'created_at',
            'sender_type'
        ).order_by('-created_at')[:10]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content[:150] + '...' if len(msg.content) > 150 else msg.content,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name()
            })

        return JsonResponse({'messages': message_list})

    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})