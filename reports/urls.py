from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('financial/', views.financial_report_page, name='financial_report_page'),  # جديد
    path('financial/json/', views.financial_report, name='financial_report'),  # API
    path('students/', views.students_report_page, name='students_report_page'),  # جديد
    path('students/json/', views.students_report, name='students_report'),  # API
    path('courses/', views.courses_report_page, name='courses_report_page'),  # جديد
    path('courses/json/', views.courses_report, name='courses_report'),  # API
    path('teachers/json/', views.teachers_report, name='teachers_report'),
]