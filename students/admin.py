from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'grade', 'year', 'balance']
    search_fields = ['name', 'phone_number']
    actions = ['delete_selected']
    
    def has_add_permission(self, request):
        return False