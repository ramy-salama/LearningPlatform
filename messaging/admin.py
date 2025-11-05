# messaging/admin.py - محدث
from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sender_type', 'receiver_type', 'is_read', 'is_reply', 'created_at', 'expires_at']
    list_filter = ['sender_type', 'receiver_type', 'is_read', 'is_reply', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'expires_at']
    list_per_page = 20
    
    fieldsets = (
        ('معلومات المرسل والمستلم', {
            'fields': ('sender_type', 'sender_id', 'receiver_type', 'receiver_id', 'course_id')
        }),
        ('محتوى الرسالة', {
            'fields': ('title', 'content', 'parent_message', 'is_reply')
        }),
        ('حالة الرسالة', {
            'fields': ('is_read', 'created_at', 'expires_at')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_type', 'user_id', 'message', 'is_read', 'created_at']
    list_filter = ['user_type', 'is_read', 'created_at']
    search_fields = ['user_type', 'user_id']
    readonly_fields = ['created_at']
    list_per_page = 20

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False