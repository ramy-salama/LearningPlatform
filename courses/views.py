from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import Course, CourseModule, Lesson
from teachers.models import Teacher
from students.models import Student
from enrollments.models import Enrollment
from django.conf import settings


# الصفحة الرئيسية
def home(request):
    courses = Course.objects.filter(status='published')[:6]  # آخر 6 كورسات
    return render(request, 'home.html', {'courses': courses})


# إنشاء كورس جديد - خاص بالمعلم فقط
@login_required
def course_create(request):
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.get(user=request.user)

            course = Course(
                teacher=teacher,
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category=request.POST.get('category'),
                price=request.POST.get('price'),
                image=request.FILES.get('image'),
                language=request.POST.get('language'),
                estimated_duration=request.POST.get('estimated_duration'),
                prerequisites=request.POST.get('prerequisites', ''),
                status='draft'
            )
            course.save()

            return redirect('course_detail', course_id=course.id)

        except Teacher.DoesNotExist:
            return render(request, 'courses/error.html', {'error': 'يجب أن تكون معلمًا لإنشاء كورس'})

    return render(request, 'courses/course_create.html')


# عرض كل الكورسات المنشورة
def course_list(request):
    courses = Course.objects.filter(status='published')
    return render(request, 'courses/course_list.html', {'courses': courses})


# صفحة تفاصيل الكورس
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'courses/course_detail.html', {'course': course})


# صفحة كورسات المعلم
@login_required
def teacher_courses(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        courses = Course.objects.filter(teacher=teacher)
        return render(request, 'courses/teacher_courses.html', {'courses': courses})
    except Teacher.DoesNotExist:
        return redirect('home')


# لوحة تحكم المعلم الخاصة بالكورس
@login_required
def course_dashboard(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.teacher.user != request.user:
        return redirect('course_detail', course_id=course_id)

    return render(request, 'courses/course_dashboard.html', {'course': course})


# عرض صفحة الدروس داخل كورس معيّن
def course_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.prefetch_related('lessons').all()

    is_enrolled = False
    student = None

    if 'student_id' in request.session:
        try:
            student = Student.objects.get(id=request.session['student_id'])
            enrollment = Enrollment.objects.filter(
                student=student,
                course=course,
                status='active'
            ).first()
            if enrollment:
                is_enrolled = True
        except Student.DoesNotExist:
            pass

    if not is_enrolled:
        return redirect('course_detail', course_id=course.id)

    lessons_by_module = []
    for module in modules:
        lessons_by_module.append({
            'module': module,
            'lessons': module.lessons.all()
        })

    return render(request, 'courses/course_lessons.html', {
        'course': course,
        'modules': modules,
        'lessons_by_module': lessons_by_module,
        'student': student
    })


# عرض تفاصيل درس معيّن (صفحة الفيديو)
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)

    has_access = False
    video_url = None
    access_message = ""
    student = None  # ⬅️ تأكد إن student بيكون defined دايماً

    if 'student_id' in request.session:
        try:
            student = Student.objects.get(id=request.session['student_id'])
            enrollment = Enrollment.objects.filter(
                student=student,
                course=course,
                status='active'
            ).first()

            has_access = bool(enrollment)

            # تحديث تقدم الطالب
            if has_access and enrollment:
                enrollment.mark_lesson_completed(lesson.id)

            if has_access and lesson.lesson_type == 'video':
                # استخدام الـ Video ID المشفر
                video_id = lesson.get_decrypted_video_id()
                if video_id:
                    has_video_access, message = lesson.check_video_access(student)
                    if has_video_access:
                        video_url = f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1"
                    else:
                        access_message = message
            elif not has_access:
                access_message = "يجب الاشتراك في الكورس لمشاهدة الدروس"

        except Student.DoesNotExist:
            access_message = "يجب تسجيل الدخول كطالب لمتابعة الدرس"
    else:
        access_message = "يجب تسجيل الدخول أولاً"

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'student': student,  # ⬅️ ده اللي كان ناقص
        'has_access': has_access,
        'video_url': video_url,
        'access_message': access_message
    })


# ✅ صفحة الفيديو المحمي
@login_required
def protected_video(request, lesson_id):
    student_id = request.session.get('student_id')
    if not student_id:
        return HttpResponse("<h2>🚫 يجب تسجيل الدخول كطالب لمشاهدة الفيديو.</h2>")

    student = get_object_or_404(Student, id=student_id)
    lesson = get_object_or_404(Lesson, id=lesson_id)

    enrollment = Enrollment.objects.filter(
        student=student,
        course=lesson.module.course,
        status='active'
    ).first()

    if not enrollment:
        return HttpResponse("<h2>🚫 غير مصرح بمشاهدة هذا الفيديو.</h2>")

    # استخدام الـ Video ID المشفر
    video_id = lesson.get_decrypted_video_id()
    if video_id:
        embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1"
        html = f"""
        <html><body style='margin:0'>
        <iframe src="{embed_url}" width="100%" height="100%"
        frameborder="0" allowfullscreen
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
        </iframe></body></html>
        """
        return HttpResponse(html)

    return HttpResponse("<h3>⚠️ لا يوجد فيديو متاح لهذا الدرس.</h3>")