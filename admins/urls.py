from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_admin_index, name='admin_dashboard'),  # ⬅️ هذا المسار الرئيسي
    path('send-bulk-message/', views.send_bulk_message, name='send_bulk_message'),
    path('send-individual-message/', views.send_individual_message, name='send_individual_message'),
    path('send-message-to-student/<int:student_id>/', views.send_message_to_student, name='send_message_to_student'),
    path('get-admin-conversations/', views.get_admin_conversations, name='get_admin_conversations'),
    path('reply-to-student/<int:message_id>/', views.reply_to_student, name='reply_to_student'),
    path('get-all-students/', views.get_all_students, name='get_all_students'),
    path('get-courses-list/', views.get_courses_list, name='get_courses_list'),
]