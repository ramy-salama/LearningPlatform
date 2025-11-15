# messaging/views.py - محدث ومصحح نهائياً
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Q
import json
from .models import Message
from students.models import Student
from teachers.models import Teacher
from admins.models import Admin
from courses.models import Course
from enrollments.models import Enrollment

@csrf_exempt
def send_message(request):
    """إرسال رسائل من جميع الأنواع - مصحح بالكامل"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # التحقق من البيانات المطلوبة
            required_fields = ['sender_type', 'sender_id', 'title', 'content']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'status': 'error', 'message': f'حقل {field} مطلوب'})

            # ✅ إصلاح مشكلة receiver_id للإدارة
            receiver_type = data.get('receiver_type', 'student')
            receiver_id = data.get('receiver_id')
            
            # إذا كان المستقبل إدارة ولم يتم تحديد receiver_id
            if receiver_type == 'admin' and not receiver_id:
                try:
                    admin_user = Admin.objects.first()  # أول مسؤول في النظام
                    receiver_id = admin_user.id if admin_user else 1
                except:
                    receiver_id = 1

            # إنشاء كائن الرسالة (باستخدام الحقول الأساسية فقط)
            message_data = {
                'sender_type': data['sender_type'],
                'sender_id': data['sender_id'],
                'title': data['title'],
                'content': data['content'],
                'receiver_type': receiver_type,
                'receiver_id': receiver_id,
                'course_id': data.get('course_id'),
                'parent_message_id': data.get('parent_message_id'),
                'is_reply': bool(data.get('parent_message_id'))
            }

            # إنشاء الرسالة
            message = Message.objects.create(**message_data)
            
            # إذا كانت رسالة جماعية، معالجة خاصة
            if data.get('receiver_type') in ['all_students', 'course_students']:
                students = []
                if data['receiver_type'] == 'all_students':
                    students = Student.objects.only('id').all()
                else:  # course_students
                    if not data.get('course_id'):
                        return JsonResponse({'status': 'error', 'message': 'معرف الكورس مطلوب'})
                    enrollments = Enrollment.objects.filter(
                        course_id=data['course_id']
                    ).select_related('student').only('student_id')
                    students = [enrollment.student for enrollment in enrollments]
                
                # إنشاء رسالة منفصلة لكل طالب
                for student in students:
                    if student.id != data['sender_id']:  # تجنب إرسال الرسالة للمرسل
                        Message.objects.create(
                            sender_type=data['sender_type'],
                            sender_id=data['sender_id'],
                            receiver_type='student',
                            receiver_id=student.id,
                            course_id=data.get('course_id'),
                            title=data['title'],
                            content=data['content']
                        )
            
            return JsonResponse({'status': 'success', 'message_id': message.id})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'بيانات JSON غير صالحة'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

def get_user_messages(request, user_type, user_id):
    """جلب رسائل المستخدم مع الردود - محسن"""
    try:
        # استعلام فعال مع prefetch_related للردود
        messages = Message.objects.filter(
            Q(receiver_type=user_type, receiver_id=user_id) |
            Q(sender_type=user_type, sender_id=user_id)
        ).exclude(
            parent_message__isnull=False  # جلب الرسائل الرئيسية فقط
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=Message.objects.only(
                    'id', 'content', 'is_read', 'created_at',
                    'sender_type', 'sender_id'
                ).order_by('created_at')
            )
        ).only(
            'id', 'title', 'content', 'is_read', 'created_at',
            'sender_type', 'sender_id', 'receiver_type', 'receiver_id'
        ).order_by('-created_at')[:50]

        message_list = []
        for msg in messages:
            message_data = {
                'id': msg.id,
                'title': msg.title,
                'content': msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name(),
                'sender_id': msg.sender_id,
                'receiver_type': msg.receiver_type,
                'receiver_name': msg.get_receiver_name(),
                'receiver_id': msg.receiver_id,
                'replies': []
            }
            
            # الردود تم جلبها مسبقاً بـ prefetch_related
            for reply in msg.replies.all():
                message_data['replies'].append({
                    'id': reply.id,
                    'content': reply.content,
                    'is_read': reply.is_read,
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M'),
                    'sender_type': reply.sender_type,
                    'sender_name': reply.get_sender_name(),
                    'sender_id': reply.sender_id
                })
            
            message_list.append(message_data)

        return JsonResponse({'messages': message_list})
    
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

def get_unread_count(request, user_type, user_id):
    """عدد الرسائل غير المقروءة - محسن"""
    try:
        count = Message.objects.filter(
            receiver_type=user_type,
            receiver_id=user_id,
            is_read=False
        ).count()
        
        return JsonResponse({'unread_count': count})
    
    except Exception as e:
        return JsonResponse({'unread_count': 0, 'error': str(e)})

def mark_as_read(request, message_id):
    """وضع علامة مقروء على الرسالة - محسن"""
    try:
        message = Message.objects.filter(id=message_id).first()
        
        if not message:
            return JsonResponse({'status': 'error', 'message': 'الرسالة غير موجودة'})
        
        message.mark_as_read()
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_conversation(request, message_id):
    """جلب محادثة كاملة مع الردود - محسن"""
    try:
        # استعلام فعال مع prefetch_related
        main_message = Message.objects.filter(
            id=message_id
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=Message.objects.only(
                    'id', 'content', 'is_read', 'created_at',
                    'sender_type', 'sender_id'
                ).order_by('created_at')
            )
        ).first()

        if not main_message:
            return JsonResponse({'conversation': []})
        
        conversation = []
        
        # إضافة الرسالة الرئيسية
        conversation.append({
            'id': main_message.id,
            'title': main_message.title,
            'content': main_message.content,
            'is_read': main_message.is_read,
            'created_at': main_message.created_at.strftime('%Y-%m-%d %H:%M'),
            'sender_type': main_message.sender_type,
            'sender_name': main_message.get_sender_name(),
            'sender_id': main_message.sender_id,
            'is_main': True
        })
        
        # إضافة الردود - تم جلبها مسبقاً
        for reply in main_message.replies.all():
            conversation.append({
                'id': reply.id,
                'content': reply.content,
                'is_read': reply.is_read,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': reply.sender_type,
                'sender_name': reply.get_sender_name(),
                'sender_id': reply.sender_id,
                'is_main': False
            })
        
        return JsonResponse({'conversation': conversation})
    
    except Exception as e:
        return JsonResponse({'conversation': [], 'error': str(e)})

# دوال مساعدة جديدة - محسنة
def get_student_messages(request, student_id):
    """جلب رسائل طالب محدد - محسن"""
    try:
        # استعلام فعال
        messages = Message.objects.filter(
            Q(receiver_type='student', receiver_id=student_id) |
            Q(sender_type='student', sender_id=student_id)
        ).only(
            'id', 'title', 'content', 'is_read', 'created_at', 'sender_type', 'sender_id'
        ).order_by('-created_at')[:20]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name()
            })
        
        return JsonResponse({'messages': message_list})
    
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

def get_teacher_messages(request, teacher_id):
    """جلب رسائل معلم محدد - محسن"""
    try:
        messages = Message.objects.filter(
            Q(receiver_type='teacher', receiver_id=teacher_id) |
            Q(sender_type='teacher', sender_id=teacher_id)
        ).only(
            'id', 'title', 'content', 'is_read', 'created_at', 'sender_type', 'sender_id'
        ).order_by('-created_at')[:20]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name()
            })
        
        return JsonResponse({'messages': message_list})
    
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

def get_admin_messages(request, admin_id):
    """جلب رسائل مسؤول محدد - محسن"""
    try:
        messages = Message.objects.filter(
            Q(receiver_type='admin', receiver_id=admin_id) |
            Q(sender_type='admin', sender_id=admin_id)
        ).only(
            'id', 'title', 'content', 'is_read', 'created_at', 'sender_type', 'sender_id'
        ).order_by('-created_at')[:20]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name()
            })
        
        return JsonResponse({'messages': message_list})
    
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

# دالة مساعدة للبحث في الرسائل
def search_messages(request, user_type, user_id):
    """بحث في رسائل المستخدم"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({'messages': [], 'error': 'كلمة البحث يجب أن تكون على الأقل حرفين'})
        
        # استعلام بحث فعال
        messages = Message.objects.filter(
            (Q(receiver_type=user_type, receiver_id=user_id) |
             Q(sender_type=user_type, sender_id=user_id)) &
            (Q(title__icontains=query) | Q(content__icontains=query))
        ).only(
            'id', 'title', 'content', 'is_read', 'created_at', 'sender_type', 'sender_id'
        ).order_by('-created_at')[:20]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'title': msg.title,
                'content': msg.content[:150] + '...' if len(msg.content) > 150 else msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'sender_type': msg.sender_type,
                'sender_name': msg.get_sender_name()
            })
        
        return JsonResponse({'messages': message_list, 'query': query})
    
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})