# messaging/context_processors.py - محدث ومحسن
from .models import Message
from students.models import Student
from teachers.models import Teacher
from admins.models import Admin

def unread_count(request):
    """
    إرجاع عدد الرسائل غير المقروءة للمستخدم الحالي
    يُستخدم في القوالب لعرض عدد الإشعارات في الهيدر
    """
    unread = 0
    
    try:
        if hasattr(request, 'user') and request.user.is_authenticated:
            # للإدارة - استخدام نموذج Admin المخصص
            if hasattr(request.user, 'is_staff') and request.user.is_staff:
                try:
                    # البحث عن مسؤول مرتبط بالمستخدم
                    admin_user = Admin.objects.filter(email=request.user.email).first()
                    if admin_user:
                        unread = Message.objects.filter(
                            receiver_type='admin',
                            receiver_id=admin_user.id,
                            is_read=False
                        ).count()
                    else:
                        # إذا لم يوجد مسؤول، استخدام ID افتراضي
                        unread = Message.objects.filter(
                            receiver_type='admin',
                            receiver_id=1,
                            is_read=False
                        ).count()
                except Exception:
                    unread = 0
            
            # للمعلمين - من خلال الجلسة
            elif hasattr(request, 'session') and 'teacher_id' in request.session:
                try:
                    teacher_id = request.session['teacher_id']
                    unread = Message.objects.filter(
                        receiver_type='teacher',
                        receiver_id=teacher_id,
                        is_read=False
                    ).count()
                except Exception:
                    unread = 0
            
            # للطلاب - من خلال الجلسة
            elif hasattr(request, 'session') and 'student_id' in request.session:
                try:
                    student_id = request.session['student_id']
                    unread = Message.objects.filter(
                        receiver_type='student',
                        receiver_id=student_id,
                        is_read=False
                    ).count()
                except Exception:
                    unread = 0
    
    except Exception:
        # في حالة أي خطأ، إرجاع صفر لمنع تعطل القوالب
        unread = 0
    
    return {'unread_count': unread}

def message_context(request):
    """
    سياق إضافي للرسائل - محسن ومعالج للأخطاء
    """
    context = {}
    
    try:
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_type = None
            user_id = None
            
            # تحديد نوع المستخدم والرقم مع معالجة الأخطاء
            if hasattr(request.user, 'is_staff') and request.user.is_staff:
                user_type = 'admin'
                try:
                    admin_user = Admin.objects.filter(email=request.user.email).first()
                    user_id = admin_user.id if admin_user else 1
                except Exception:
                    user_id = 1
            
            elif hasattr(request, 'session'):
                if 'teacher_id' in request.session:
                    user_type = 'teacher'
                    user_id = request.session['teacher_id']
                elif 'student_id' in request.session:
                    user_type = 'student'
                    user_id = request.session['student_id']
            
            # جلب الرسائل إذا تم تحديد المستخدم
            if user_type and user_id:
                try:
                    # جلب آخر 5 رسائل غير مقروءة مع معالجة الأخطاء
                    recent_messages = Message.objects.filter(
                        receiver_type=user_type,
                        receiver_id=user_id,
                        is_read=False
                    ).select_related().order_by('-created_at')[:5]
                    
                    # تحضير بيانات الرسائل بشكل آمن
                    messages_data = []
                    for msg in recent_messages:
                        try:
                            messages_data.append({
                                'id': msg.id,
                                'title': msg.title,
                                'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                                'created_at': msg.created_at,
                                'sender_name': msg.get_sender_name(),
                                'is_read': msg.is_read
                            })
                        except Exception:
                            continue
                    
                    context['recent_messages'] = messages_data
                    
                except Exception as e:
                    # في حالة خطأ في جلب الرسائل، تعيين قائمة فارغة
                    context['recent_messages'] = []
                    print(f"Error loading messages: {e}")
    
    except Exception as e:
        # منع أي أخطاء من التأثير على القوالب
        context['recent_messages'] = []
        print(f"Error in message_context: {e}")
    
    return context

def admin_messaging_context(request):
    """
    سياق إضافي لصفحات الإدارة - يحسن تجربة المراسلة
    """
    context = {}
    
    try:
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            # إحصائيات سريعة للإدارة
            try:
                total_students = Student.objects.count()
                total_teachers = Teacher.objects.count()
                pending_teachers = Teacher.objects.filter(status='pending').count()
                
                context['admin_stats'] = {
                    'total_students': total_students,
                    'total_teachers': total_teachers,
                    'pending_teachers': pending_teachers
                }
            except Exception:
                context['admin_stats'] = {
                    'total_students': 0,
                    'total_teachers': 0,
                    'pending_teachers': 0
                }
            
            # رسائل الإدارة غير المقروءة
            try:
                admin_messages = Message.objects.filter(
                    receiver_type='admin',
                    is_read=False
                ).count()
                context['admin_unread_messages'] = admin_messages
            except Exception:
                context['admin_unread_messages'] = 0
    
    except Exception:
        # قيم افتراضية في حالة الخطأ
        context['admin_stats'] = {
            'total_students': 0,
            'total_teachers': 0,
            'pending_teachers': 0
        }
        context['admin_unread_messages'] = 0
    
    return context

# تحديث context_processors في settings.py إذا لزم الأمر
"""
# في edu_platform/settings.py - تأكد من إضافة:
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'messaging.context_processors.unread_count',
                'messaging.context_processors.message_context',
                'messaging.context_processors.admin_messaging_context',  # جديد
            ],
        },
    },
]
"""