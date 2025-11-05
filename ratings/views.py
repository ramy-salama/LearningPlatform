from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import CourseRating, TeacherRating
from courses.models import Course
from teachers.models import Teacher
from students.models import Student
from django.db import models
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def submit_course_rating(request, course_id):
    if 'student_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'يجب تسجيل الدخول'})
    
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=request.session['student_id'])
            course = get_object_or_404(Course, id=course_id)
            rating = request.POST.get('rating')
            review = request.POST.get('review', '')
            
            rating_obj, created = CourseRating.objects.get_or_create(
                student=student,
                course=course,
                defaults={'rating': rating, 'review': review}
            )
            
            if not created:
                rating_obj.rating = rating
                rating_obj.review = review
                rating_obj.save()
            
            return JsonResponse({'success': True, 'message': 'تم إضافة التقييم بنجاح'})
            
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'يجب أن تكون طالبًا'})

def get_course_ratings(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    ratings = CourseRating.objects.filter(course=course)
    
    average = ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
    total_ratings = ratings.count()
    
    return JsonResponse({
        'average_rating': round(average, 1),
        'total_ratings': total_ratings,
        'ratings': list(ratings.values('student__name', 'rating', 'review', 'created_at'))
    })

@csrf_exempt
def submit_teacher_rating(request, teacher_id):
    if 'student_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'يجب تسجيل الدخول'})
    
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=request.session['student_id'])
            teacher = get_object_or_404(Teacher, id=teacher_id)
            rating = request.POST.get('rating')
            review = request.POST.get('review', '')
            
            rating_obj, created = TeacherRating.objects.get_or_create(
                student=student,
                teacher=teacher,
                defaults={'rating': rating, 'review': review}
            )
            
            if not created:
                rating_obj.rating = rating
                rating_obj.review = review
                rating_obj.save()
            
            return JsonResponse({'success': True, 'message': 'تم تقييم المعلم بنجاح'})
            
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'يجب أن تكون طالبًا'})

def get_teacher_ratings(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    ratings = TeacherRating.objects.filter(teacher=teacher)
    
    average = ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
    total_ratings = ratings.count()
    
    return JsonResponse({
        'average_rating': round(average, 1),
        'total_ratings': total_ratings,
        'ratings': list(ratings.values('student__name', 'rating', 'review', 'created_at'))
    })