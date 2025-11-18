# students/views.py - محدث ومصحح مع إضافة المراسلة السريعة
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Prefetch
import json
from .models import Student
from enrollments.models import Enrollment
from messaging.models import Message
from courses.models import Course
from decimal import Decimal, InvalidOperation
from admins.models import Admin  # ✅ استيراد نموذج Admin
from django.http import HttpResponse

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
# دالة المراسلة الجديدة (مصححة بالكامل)
# ===============================
@csrf_exempt
def send_student_message(request):
    """إرسال رسالة من الطالب إلى الإدارة - مصحح بالكامل"""
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

            # ✅ التحقق من طول المحتوى (150 حرف كحد أقصى)
            if len(data['content']) > 150:
                return JsonResponse({'status': 'error', 'message': 'الرسالة يجب ألا تزيد عن 150 حرف'})

            # ✅ إصلاح المشكلة: الحصول على أول مسؤول كـ receiver_id
            try:
                admin_user = Admin.objects.first()  # أول مسؤول في النظام
                admin_id = admin_user.id if admin_user else 1  # استخدام 1 إذا لم يوجد مسؤول
            except:
                admin_id = 1  # قيمة افتراضية

            # ✅ إنشاء الرسالة مع receiver_id محددة للإدارة
            message = Message.objects.create(
                sender_type='student',
                sender_id=student_id,
                receiver_type='admin',
                receiver_id=admin_id,  # ✅ الآن receiver_id محدد
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
