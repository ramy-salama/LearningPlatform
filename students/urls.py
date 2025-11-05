# students/urls.py - محدث ومصحح
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # المسارات الأساسية (موجودة مسبقاً)
    path('register/', views.student_register, name='student_register'),
    path('login/', views.student_login, name='student_login'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('wallet/topup/', views.wallet_topup, name='wallet_topup'),
    path('wallet/balance/', views.wallet_balance, name='wallet_balance'),
    path('logout/', views.student_logout, name='student_logout'),
    
    # مسارات المراسلة الجديدة
    path('send-message/', views.send_student_message, name='send_student_message'),
    path('notifications/', views.get_student_notifications, name='student_notifications'),
    path('unread-messages/', views.get_unread_student_messages, name='unread_student_messages'),
    path('conversation/<int:message_id>/', views.get_student_conversation, name='student_conversation'),
]