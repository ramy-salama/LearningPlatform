import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_platform.settings')
django.setup()

from students.models import Student

students_data = [
    {'name': 'أحمد محمد', 'phone_number': '01010000001', 'parent_phone': '01020000001', 'password': '123456', 'residence': 'القاهرة', 'grade': 'primary', 'year': 'first', 'balance': 500},
    {'name': 'مريم علي', 'phone_number': '01010000002', 'parent_phone': '01020000002', 'password': '123456', 'residence': 'الجيزة', 'grade': 'preparatory', 'year': 'second', 'balance': 300},
    {'name': 'ياسمين خالد', 'phone_number': '01010000003', 'parent_phone': '01020000003', 'password': '123456', 'residence': 'الإسكندرية', 'grade': 'secondary', 'year': 'third', 'balance': 700},
]

for data in students_data:
    Student.objects.create(**data)

print("تم إنشاء 3 طلاب تجريبيين بنجاح")