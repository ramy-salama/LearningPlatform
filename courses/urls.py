from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # روابط الكورسات العامة
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    
    # روابط المعلم
    path('create/', views.course_create, name='course_create'),
    path('my-courses/', views.teacher_courses, name='teacher_courses'),
    path('<int:course_id>/dashboard/', views.course_dashboard, name='course_dashboard'),
    
    # روابط الفيديو المحمي والدرس
    path('lesson/<int:lesson_id>/video/', views.protected_video, name='protected_video'),
    path('<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),  # هذا السطر موجود
    
    # السطر الناقص علشان صفحة الدروس
    path('<int:course_id>/lessons/', views.course_lessons, name='course_lessons'),  # أضف هذا السطر
]