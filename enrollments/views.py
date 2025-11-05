from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Enrollment
from students.models import Student
from courses.models import Course

def enroll_course(request, course_id):
    if 'student_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'يجب تسجيل الدخول أولاً'})
    
    try:
        student = Student.objects.get(id=request.session['student_id'])
        course = get_object_or_404(Course, id=course_id)
        
        # تحقق إذا الرصيد كافي
        if student.balance < course.price:
            return JsonResponse({
                'success': False, 
                'message': f'رصيدك غير كافي. السعر: {course.price} جنيه، رصيدك: {student.balance} جنيه'
            })
        
        # تحقق إذا مسجل من قبل في حالة active فقط
        existing_enrollment = Enrollment.objects.filter(
            student=student, 
            course=course,
            status='active'
        ).first()
        
        if existing_enrollment:
            return JsonResponse({
                'success': False, 
                'message': 'أنت مسجل في هذا الكورس بالفعل'
            })
        
        # خصم المبلغ من رصيد الطالب
        student.balance -= course.price
        student.total_spent += course.price
        student.save()
        
        # إنشاء الحجز
        enrollment = Enrollment(
            student=student,
            course=course,
            amount_paid=course.price,
            status='active',
            payment_status='paid'
        )
        enrollment.save()
        
        # زيادة عدد الطلاب في الكورس
        course.students_count += 1
        course.save()
        
        # ⬇️ الحل: توجيه مباشر بدون AJAX
        return JsonResponse({
            'success': True, 
            'message': f'🎉 تم شراء الكورس "{course.title}" بنجاح!',
            'redirect_url': '/students/dashboard/'
        })
        
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'يجب أن تكون طالباً'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'حدث خطأ: {str(e)}'})

def student_enrollments(request):
    if 'student_id' not in request.session:
        return redirect('/students/login/')
    
    try:
        student = Student.objects.get(id=request.session['student_id'])
        enrollments = Enrollment.objects.filter(student=student).select_related('course', 'course__teacher')
        return render(request, 'enrollments/student_enrollments.html', {'enrollments': enrollments})
    except Student.DoesNotExist:
        return redirect('/students/login/')

def enrollment_detail(request, enrollment_id):
    if 'student_id' not in request.session:
        return redirect('/students/login/')
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student_id=request.session['student_id'])
    return render(request, 'enrollments/enrollment_detail.html', {'enrollment': enrollment})