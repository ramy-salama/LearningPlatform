# teachers/urls.py - محدث ومصحح (بدون نظام المراسلة)
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # المسارات الأساسية فقط
    path('register/', views.teacher_register, name='teacher_register'),
    path('login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('<int:teacher_id>/', views.teacher_profile, name='teacher_profile'),
]