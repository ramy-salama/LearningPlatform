# teachers/urls.py - محدث ومصحح
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # المسارات الأساسية (موجودة مسبقاً)
    path('register/', views.teacher_register, name='teacher_register'),
    path('login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('<int:teacher_id>/', views.teacher_profile, name='teacher_profile'),
    
    # مسارات المراسلة الجديدة
    path('send-message/', views.send_teacher_message, name='send_teacher_message'),
    path('courses/', views.get_teacher_courses, name='teacher_courses'),
    path('notifications/', views.get_teacher_notifications, name='teacher_notifications'),
    path('unread-count/', views.get_teacher_unread_count, name='teacher_unread_count'),
    path('read/<int:message_id>/', views.mark_teacher_message_read, name='mark_teacher_message_read'),
]