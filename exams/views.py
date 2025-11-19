from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import json
from teachers.decorators import teacher_required
from teachers.models import Teacher
from courses.models import Course
from .models import Exam, Question, Choice, Result
from django.utils import timezone
from students.models import Student
from enrollments.models import Enrollment
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.template.defaulttags import register

@teacher_required
def create_exam(request):
    teacher_id = request.session.get('teacher_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    teacher_courses = Course.objects.filter(teacher=teacher)
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        title = request.POST.get('title')
        instructions = request.POST.get('instructions')
        duration = request.POST.get('duration')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        points_per_question = request.POST.get('points_per_question')
        
        if not all([course_id, title, instructions, duration, start_date, end_date]):
            messages.error(request, "جميع الحقول مطلوبة")
            return render(request, 'exams/exam_create.html', {'courses': teacher_courses})
        
        try:
            course = Course.objects.get(id=course_id, teacher=teacher)
            exam = Exam.objects.create(
                course=course,
                teacher=teacher,
                title=title,
                instructions=instructions,
                duration=duration,
                start_date=start_date,
                end_date=end_date,
                points_per_question=points_per_question or 1,
                is_active=False  # غير نشط حتى يتم إضافة الأسئلة
            )
            messages.success(request, "تم إنشاء الاختبار بنجاح. يمكنك الآن إضافة الأسئلة")
            return redirect('exams:exam_questions', exam_id=exam.id)
        except Exception as e:
            messages.error(request, f"حدث خطأ: {str(e)}")
    
    return render(request, 'exams/exam_create.html', {'courses': teacher_courses})

@teacher_required
def exam_questions(request, exam_id):
    teacher_id = request.session.get('teacher_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    try:
        exam = Exam.objects.get(id=exam_id, teacher=teacher)
    except Exam.DoesNotExist:
        messages.error(request, "غير مصرح لك بالوصول لهذا الاختبار")
        return redirect('teachers:teacher_dashboard')
    
    if exam.start_date <= timezone.now():
        messages.error(request, "لا يمكن تعديل الاختبار بعد بدء ظهوره")
        return redirect('exams:exam_management')
    
    questions = Question.objects.filter(exam=exam).order_by('order')
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # معالجة AJAX لحفظ الأسئلة باستخدام FormData
        try:
            question_text = request.POST.get('question_text')
            choices_json = request.POST.get('choices')
            correct_choice_index = request.POST.get('correct_choice_index')
            
            if not question_text or not choices_json or correct_choice_index is None:
                return JsonResponse({'success': False, 'error': 'بيانات غير مكتملة'})
            
            # تحويل JSON إلى قائمة
            choices = json.loads(choices_json)
            
            if len(choices) != 4:
                return JsonResponse({'success': False, 'error': 'يجب إدخال 4 اختيارات'})
            
            # إنشاء السؤال
            question = Question.objects.create(
                exam=exam,
                text=question_text,
                order=questions.count() + 1
            )
            
            # حفظ صورة السؤال إذا وجدت
            if 'question_image' in request.FILES:
                question.image = request.FILES['question_image']
                question.save()
            
            # إنشاء الاختيارات
            for i, choice_text in enumerate(choices):
                Choice.objects.create(
                    question=question,
                    text=choice_text,
                    is_correct=(i == int(correct_choice_index))
                )
            
            return JsonResponse({'success': True, 'question_id': question.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'exams/exam_questions.html', {
        'exam': exam,
        'questions': questions
    })

@teacher_required
def exam_management(request):
    teacher_id = request.session.get('teacher_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    exams = Exam.objects.filter(teacher=teacher).order_by('-created_at')
    
    return render(request, 'exams/exam_manage.html', {'exams': exams})

@teacher_required
def delete_question(request, question_id):
    teacher_id = request.session.get('teacher_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    try:
        question = Question.objects.get(id=question_id, exam__teacher=teacher)
        
        # منع الحذف إذا بدأ الاختبار
        if question.exam.start_date <= timezone.now():
            return JsonResponse({'success': False, 'error': 'لا يمكن حذف السؤال بعد بدء الاختبار'})
        
        question.delete()
        return JsonResponse({'success': True})
        
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'السؤال غير موجود'})

def student_exams(request):
    """عرض الاختبارات المتاحة للطالب"""
    if not request.session.get('student_id'):
        return redirect('students:student_login')
    
    student_id = request.session.get('student_id')
    student = Student.objects.get(id=student_id)
    
    # جلب الكورسات المسجلة للطالب
    enrollments = Enrollment.objects.filter(
        student=student, 
        status='active'
    ).select_related('course')
    
    # ⭐ التصحيح - اطبع المعلومات
    print("🔍 [DEBUG] معلومات الطالب والكورسات:")
    print(f"الطالب: {student.name} (ID: {student.id})")
    print("الكورسات المسجلة:")
    for enrollment in enrollments:
        print(f"- {enrollment.course.title} (ID: {enrollment.course.id})")
    
    # جلب الاختبارات النشطة لهذه الكورسات
    active_exams = []
    for enrollment in enrollments:
        exams = Exam.objects.filter(course=enrollment.course)
        
        print(f"🔍 [DEBUG] الكورس {enrollment.course.title}:")
        
        for exam in exams:
            # التحقق من توفر الاختبار مباشرة
            now = timezone.now()
            is_available = (
                exam.is_active and 
                exam.question_set.count() >= 10 and
                exam.start_date <= now <= exam.end_date
            )
            
            print(f"   الاختبار: {exam.title}")
            print(f"   - is_active: {exam.is_active}")
            print(f"   - عدد الأسئلة: {exam.question_set.count()}")
            print(f"   - start_date: {exam.start_date}")
            print(f"   - end_date: {exam.end_date}")
            print(f"   - الوقت الحالي: {now}")
            print(f"   - متاح: {is_available}")
            
            if is_available:
                result = Result.objects.filter(exam=exam, student=student).first()
                active_exams.append({
                    'exam': exam,
                    'enrollment': enrollment,
                    'result': result
                })
    
    print(f"🔍 [DEBUG] عدد الاختبارات المتاحة: {len(active_exams)}")
    
    return render(request, 'exams/student_exams.html', {
        'student': student,
        'active_exams': active_exams
    })



def take_exam(request, exam_id):
    """صفحة أداء الاختبار"""
    # التحقق من تسجيل الدخول
    if not request.session.get('student_id'):
        return redirect('students:student_login')
    
    student_id = request.session.get('student_id')
    student = Student.objects.get(id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    
    # التحقق من صلاحية الاختبار
    if not exam.is_active or exam.start_date > timezone.now() or exam.end_date < timezone.now():
        return render(request, 'exams/exam_error.html', {
            'error': 'هذا الاختبار غير متاح حالياً'
        })
    
    # التحقق من تسجيل الطالب في الكورس
    enrollment = Enrollment.objects.filter(
        student=student,
        course=exam.course,
        status='active'
    ).first()
    
    if not enrollment:
        return render(request, 'exams/exam_error.html', {
            'error': 'غير مسجل في هذا الكورس'
        })
    
    # التحقق إذا كان الطالب قد أدى الاختبار مسبقاً
    existing_result = Result.objects.filter(exam=exam, student=student).first()
    if existing_result:
        return redirect('exams:exam_result', exam_id=exam.id)
    
    # جلب الأسئلة مرتبة
    questions = Question.objects.filter(exam=exam).order_by('order').prefetch_related('choice_set')
    
    # ✅ حفظ وقت بدء الاختبار
    request.session['exam_start_time'] = str(timezone.now())
    
    return render(request, 'exams/take_exam.html', {
        'exam': exam,
        'questions': questions,
        'student': student,
        'duration_minutes': exam.duration
    })

def submit_exam(request, exam_id):
    if not request.session.get('student_id'):
        return redirect('students:student_login')
    
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        student = Student.objects.get(id=student_id)
        exam = get_object_or_404(Exam, id=exam_id)
        
        # جلب الإجابات من الـ JSON
        answers_data = request.POST.get('answers_data')
        if not answers_data:
            return redirect('exams:student_exams')
        
        try:
            answers = json.loads(answers_data)
        except json.JSONDecodeError:
            return redirect('exams:student_exams')
        
        # حساب الدرجة
        score = 0
        total_questions = exam.question_set.count()
        
        for question in exam.question_set.all():
            selected_choice_id = answers.get(str(question.id))
            
            if selected_choice_id:
                try:
                    selected_choice = Choice.objects.get(id=selected_choice_id, question=question)
                    if selected_choice.is_correct:
                        score += exam.points_per_question
                except Choice.DoesNotExist:
                    pass
        
        # حساب النسبة المئوية
        total_points = total_questions * exam.points_per_question
        percentage = (score / total_points) * 100 if total_points > 0 else 0
        
        # ✅ جلب وقت البداية من session
        start_time_str = request.session.get('exam_start_time')
        if start_time_str:
            started_at = timezone.datetime.fromisoformat(start_time_str)
        else:
            started_at = timezone.now()
        
        # ✅ حفظ النتيجة مع الوقت
        Result.objects.create(
            exam=exam,
            student=student,
            score=score,
            percentage=percentage,
            answers=answers,
            started_at=started_at,
            completed_at=timezone.now()
        )
        
        # ✅ مسح وقت البدء من session
        if 'exam_start_time' in request.session:
            del request.session['exam_start_time']
        
        return redirect('exams:exam_result', exam_id=exam.id)
    
    return redirect('exams:student_exams')

def exam_result(request, exam_id):
    """عرض نتيجة الاختبار"""
    # التحقق من تسجيل الدخول
    if not request.session.get('student_id'):
        return redirect('students:student_login')
    
    student_id = request.session.get('student_id')
    student = Student.objects.get(id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    result = get_object_or_404(Result, exam=exam, student=student)
    
    return render(request, 'exams/exam_result.html', {
        'exam': exam,
        'result': result,
        'student': student
    })

def wrong_answers_api(request, exam_id, student_id):
    """API لجلب الإجابات الخاطئة"""
    try:
        exam = Exam.objects.get(id=exam_id)
        student = Student.objects.get(id=student_id)
        result = Result.objects.get(exam=exam, student=student)
        
        wrong_answers = []
        
        for question in exam.question_set.all():
            student_choice_id = result.answers.get(str(question.id))
            
            if student_choice_id:
                try:
                    student_choice = Choice.objects.get(id=student_choice_id)
                    correct_choice = question.choice_set.filter(is_correct=True).first()
                    
                    if student_choice != correct_choice:
                        wrong_answers.append({
                            'question_text': question.text,
                            'question_image': question.image.url if question.image else None,
                            'student_answer': student_choice.text,
                            'correct_answer': correct_choice.text if correct_choice else 'غير محدد'
                        })
                except Choice.DoesNotExist:
                    pass
        
        return JsonResponse({
            'wrong_answers': wrong_answers
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

# دالة جديدة لفحص وجود اختبارات نشطة في الكورس
def check_course_has_active_exams(course_id):
    """فحص إذا كان الكورس به اختبارات نشطة"""
    now = timezone.now()
    has_active_exams = Exam.objects.filter(
        course_id=course_id,
        is_active=True,
        question_set__count__gte=10,
        start_date__lte=now,
        end_date__gte=now
    ).exists()
    return has_active_exams



@register.filter
def get_question_text(question_id):
    try:
        return Question.objects.get(id=question_id).text
    except Question.DoesNotExist:
        return "سؤال محذوف"

@teacher_required
def exam_results_stats(request, exam_id):
    teacher_id = request.session.get('teacher_id')
    teacher = Teacher.objects.get(id=teacher_id)
    
    exam = get_object_or_404(Exam, id=exam_id, teacher=teacher)
    results = Result.objects.filter(exam=exam).select_related('student')
    
    # الإحصائيات
    total_students = results.count()
    avg_percentage = results.aggregate(avg=Avg('percentage'))['avg'] or 0
    passed_students = results.filter(percentage__gte=50).count()
    failed_students = total_students - passed_students
    
    # الأسئلة الأكثر خطأ
    wrong_questions = {}
    for result in results:
        for q_id, choice_id in result.answers.items():
            question = Question.objects.get(id=int(q_id))
            choice = Choice.objects.get(id=choice_id)
            if not choice.is_correct:
                wrong_questions[question.id] = wrong_questions.get(question.id, 0) + 1
    
    # تحضير البيانات للتمبلت
    top_wrong_questions = []
    for question_id, wrong_count in sorted(wrong_questions.items(), key=lambda x: x[1], reverse=True)[:5]:
        question = Question.objects.get(id=question_id)
        top_wrong_questions.append({
            'question_text': question.text,
            'wrong_count': wrong_count
        })
    
    return render(request, 'exams/exam_results_stats.html', {
        'exam': exam,
        'results': results,
        'total_students': total_students,
        'avg_percentage': round(avg_percentage, 1),
        'passed_students': passed_students,
        'failed_students': failed_students,
        'top_wrong_questions': top_wrong_questions,
    })