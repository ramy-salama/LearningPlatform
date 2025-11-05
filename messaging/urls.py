# messaging/urls.py - محدث ومصحح
from django.urls import path
from . import views

urlpatterns = [
    # إرسال الرسائل
    path('send/', views.send_message, name='send_message'),
    
    # جلب الرسائل
    path('messages/<str:user_type>/<int:user_id>/', views.get_user_messages, name='get_messages'),
    
    # جلب رسائل طالب محدد
    path('student/<int:student_id>/messages/', views.get_student_messages, name='get_student_messages'),
    
    # عدد الرسائل غير المقروءة
    path('unread/<str:user_type>/<int:user_id>/', views.get_unread_count, name='unread_count'),
    
    # وضع علامة مقروء
    path('read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
    
    # جلب محادثة كاملة
    path('conversation/<int:message_id>/', views.get_conversation, name='get_conversation'),
]