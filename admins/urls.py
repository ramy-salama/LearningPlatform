# admins/urls.py - محدث ومكتمل
from django.urls import path
from . import views

urlpatterns = [
    # مسارات المراسلة الجديدة
    path('send-bulk/', views.send_bulk_message, name='send_bulk_message'),
    path('send-individual/', views.send_individual_message, name='send_individual_message'),
    path('send-to-student/<int:student_id>/', views.send_message_to_student, name='send_message_to_student'),
    path('conversations/', views.get_admin_conversations, name='admin_conversations'),
    path('reply/<int:message_id>/', views.reply_to_student, name='reply_to_student'),
    path('students-list/', views.get_all_students, name='get_all_students'),
    path('courses-list/', views.get_courses_list, name='get_courses_list'),
]