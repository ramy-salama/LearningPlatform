# admins/views.py - محدث ومصحح
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
from students.models import Student
from courses.models import Course
from enrollments.models import Enrollment
from messaging.models import Message

@csrf_exempt
def send_bulk_message(request):
    """إرسال رسالة جماعية من الإدارة"""
    if request.method == 'POST':
        try:
            # التحقق من صلاحية الإدارة
            if not hasattr(request.user, 'admin'):
                return JsonResponse({'status': 'error', 'message': 'صلاحية غير متاحة'})

            data = json.loads(request.body)
            admin_id = request.user.admin.id

            # التحقق من البيانات المطلوبة
            if 'recipient_type' not in data or 'title' not in data or 'content' not in data:
                return JsonResponse({'status': 'error', 'message': 'بيانات غير مكتملة'})

            # تحديد المستلمين
            students = []
            if data['recipient_type'] == 'all_students':
                students = Student.objects.all()
            elif data['recipient_type'] == 'course_students':
                if 'course_id' not in data:
                    return JsonResponse({'status': 'error', 'message': 'معرف الكورس مطلوب'})
                course = Course.objects.get(id=data['course_id'])
                enrollments = Enrollment.objects.filter(course=course)
                students = [enrollment.student for enrollment in enrollments]
            else:  # individual
                if 'receiver_id' not in data:
                    return JsonResponse({'status': 'error', 'message': 'معرف الطالب مطلوب'})
                students = [Student.objects.get(id=data['receiver_id'])]

            # إنشاء الرسالة لكل طالب
            for student in students:
                Message.objects.create(
                    sender_type='admin',
                    sender_id=admin_id,
                    receiver_type='student',
                    receiver_id=student.id,
                    course_id=data.get('course_id'),
                    title=data['title'],
                    content=data['content']
                )

            return JsonResponse({'status': 'success', 'message': f'تم إرسال الرسالة إلى {len(students)} طالب'})

        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الطالب غير موجود'})
        except Course.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الكورس غير موجود'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

@csrf_exempt
def send_individual_message(request):
    """إرسال رسالة فردية من الإدارة لطالب محدد"""
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'admin'):
                return JsonResponse({'status': 'error', 'message': 'صلاحية غير متاحة'})

            data = json.loads(request.body)
            admin_id = request.user.admin.id

            # التحقق من البيانات المطلوبة
            if 'student_id' not in data or 'title' not in data or 'content' not in data:
                return JsonResponse({'status': 'error', 'message': 'بيانات غير مكتملة'})

            message = Message.objects.create(
                sender_type='admin',
                sender_id=admin_id,
                receiver_type='student',
                receiver_id=data['student_id'],
                title=data['title'],
                content=data['content']
            )

            return JsonResponse({'status': 'success', 'message_id': message.id})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

@csrf_exempt
def send_message_to_student(request, student_id):
    """إرسال رسالة مباشرة لطالب من خلال أيقونة في الداشبورد"""
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'admin'):
                return JsonResponse({'status': 'error', 'message': 'صلاحية غير متاحة'})

            data = json.loads(request.body)
            admin_id = request.user.admin.id

            # التحقق من وجود الطالب
            student = Student.objects.get(id=student_id)

            # التحقق من البيانات المطلوبة
            if 'title' not in data or 'content' not in data:
                return JsonResponse({'status': 'error', 'message': 'العنوان والمحتوى مطلوبان'})

            message = Message.objects.create(
                sender_type='admin',
                sender_id=admin_id,
                receiver_type='student',
                receiver_id=student_id,
                title=data['title'],
                content=data['content']
            )

            return JsonResponse({'status': 'success', 'message': f'تم إرسال الرسالة إلى {student.name}', 'message_id': message.id})

        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الطالب غير موجود'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

def get_admin_conversations(request):
    """جلب محادثات الإدارة مع الطلاب"""
    try:
        if not hasattr(request.user, 'admin'):
            return JsonResponse({'conversations': []})

        admin_id = request.user.admin.id
        
        # جلب الرسائل المرسلة من الإدارة أو المستلمة للإدارة
        messages = Message.objects.filter(
            Q(sender_type='admin', sender_id=admin_id) |
            Q(receiver_type='admin', receiver_id=admin_id)
        ).exclude(is_reply=True).order_by('-created_at')[:20]

        conversations = []
        for msg in messages:
            conversations.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name(),
                'receiver_type': msg.receiver_type,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'has_replies': msg.replies.exists()
            })

        return JsonResponse({'conversations': conversations})

    except Exception as e:
        return JsonResponse({'conversations': [], 'error': str(e)})

@csrf_exempt
def reply_to_student(request, message_id):
    """رد الإدارة على رسالة طالب"""
    if request.method == 'POST':
        try:
            if not hasattr(request.user, 'admin'):
                return JsonResponse({'status': 'error', 'message': 'صلاحية غير متاحة'})

            data = json.loads(request.body)
            admin_id = request.user.admin.id
            original_message = Message.objects.get(id=message_id)

            # التحقق من محتوى الرد
            if 'content' not in data or not data['content'].strip():
                return JsonResponse({'status': 'error', 'message': 'محتوى الرد مطلوب'})

            reply = Message.objects.create(
                sender_type='admin',
                sender_id=admin_id,
                receiver_type='student',
                receiver_id=original_message.sender_id,
                title=f"رد على: {original_message.title}",
                content=data['content'],
                parent_message=original_message,
                is_reply=True
            )

            return JsonResponse({'status': 'success', 'reply_id': reply.id})

        except Message.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الرسالة الأصلية غير موجودة'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

# دوال جديدة للمراسلة من لوحة الإدارة
def get_all_students(request):
    """جلب قائمة جميع الطلاب للمراسلة الفردية"""
    try:
        students = Student.objects.all().values('id', 'name', 'phone_number')
        return JsonResponse({'students': list(students)})
    except Exception as e:
        return JsonResponse({'students': [], 'error': str(e)})

def get_courses_list(request):
    """جلب قائمة الكورسات للمراسلة الجماعية"""
    try:
        courses = Course.objects.filter(status='published').values('id', 'title')
        return JsonResponse({'courses': list(courses)})
    except Exception as e:
        return JsonResponse({'courses': [], 'error': str(e)})