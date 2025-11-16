# admins/urls.py - محدث مع إضافة مسار رسائل الإدارة
from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_admin_index, name='admin_dashboard'),  # ⬅️ هذا المسار الرئيسي

    # ✅ مسارات جديدة للرسائل الحقيقية
    path('get_admin_notifications/', views.get_admin_notifications, name='get_admin_notifications'),
    path('get_current_admin/', views.get_current_admin, name='get_current_admin'),

    path('mark-message-read/<int:message_id>/', views.mark_message_as_read, name='mark_message_read'),
]



