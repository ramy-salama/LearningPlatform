from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('financial/', views.financial_report_page, name='financial_report_page'),
    path('financial/json/', views.financial_report, name='financial_report'),
    path('students/', views.students_report_page, name='students_report_page'),
    path('students/json/', views.students_report, name='students_report'),
    path('courses/', views.courses_report_page, name='courses_report_page'),
    path('courses/json/', views.courses_report, name='courses_report'),
    path('teachers/json/', views.teachers_report, name='teachers_report'),
    path('dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),  # جديد
]