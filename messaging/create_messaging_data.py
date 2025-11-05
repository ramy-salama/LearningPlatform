# messaging/management/commands/create_messaging_data.py
from django.core.management.base import BaseCommand
from messaging.models import Message, Notification
from students.models import Student
from teachers.models import Teacher
from admins.models import Admin
from courses.models import Course
from enrollments.models import Enrollment
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية لنظام المراسلة المحدث'

    def handle(self, *args, **options):
        # تنظيف البيانات القديمة
        Message.objects.all().delete()
        Notification.objects.all().delete()
        
        self.stdout.write('🗑️ تم تنظيف البيانات القديمة')
        
        # إنشاء بيانات تجريبية إذا لم تكن موجودة
        self.create_sample_data()
        
        # إنشاء رسائل تجريبية
        self.create_sample_messages()
        
        self.stdout.write(
            self.style.SUCCESS('✅ تم إنشاء بيانات تجريبية لنظام المراسلة بنجاح')
        )

    def create_sample_data(self):
        """إنشاء بيانات عينة إذا لم تكن موجودة"""
        
        # إنشاء مسؤول إذا لم يكن موجوداً
        if not Admin.objects.exists():
            Admin.objects.create(
                name="المسؤول الرئيسي",
                email="admin@eduplatform.com",
                password="admin123",
                phone_number="01000000001",
                permissions="super_admin"
            )
            self.stdout.write('👤 تم إنشاء المسؤول الرئيسي')
        
        # إنشاء طلاب عينة إذا لم يكونوا موجودين
        if not Student.objects.exists():
            students_data = [
                {
                    'name': 'أحمد محمد',
                    'phone_number': '01010000001',
                    'parent_phone': '01010000002',
                    'password': 'student123',
                    'residence': 'القاهرة',
                    'grade': 'secondary',
                    'year': 'first'
                },
                {
                    'name': 'فاطمة علي',
                    'phone_number': '01010000003', 
                    'parent_phone': '01010000004',
                    'password': 'student123',
                    'residence': 'الجيزة',
                    'grade': 'preparatory',
                    'year': 'second'
                },
                {
                    'name': 'يوسف محمود',
                    'phone_number': '01010000005',
                    'parent_phone': '01010000006',
                    'password': 'student123', 
                    'residence': 'الإسكندرية',
                    'grade': 'primary',
                    'year': 'fifth'
                }
            ]
            
            for student_data in students_data:
                Student.objects.create(**student_data)
            self.stdout.write('🎓 تم إنشاء 3 طلاب عينة')
        
        # إنشاء معلمين عينة إذا لم يكونوا موجودين
        if not Teacher.objects.exists():
            teachers_data = [
                {
                    'name': 'دكتور محمد أحمد',
                    'phone_number': '01020000001',
                    'email': 'math.teacher@eduplatform.com',
                    'password': 'teacher123',
                    'address': 'القاهرة - مصر الجديدة',
                    'bio': 'معلم رياضيات بخبرة 10 سنوات في التدريس',
                    'specialization': 'الرياضيات',
                    'teaching_levels': 'primary,preparatory,secondary',
                    'experience': 'خبرة 10 سنوات في تدريس الرياضيات',
                    'degree': 'master',
                    'major': 'الرياضيات التطبيقية',
                    'certificates': 'شهادة تدريس معتمدة',
                    'payment_method': 'vodafone_cash',
                    'account_number': '01020000001',
                    'profit_percentage': 60,
                    'status': 'approved'
                },
                {
                    'name': 'أستاذة سارة عبدالله',
                    'phone_number': '01020000002',
                    'email': 'science.teacher@eduplatform.com', 
                    'password': 'teacher123',
                    'address': 'الجيزة - الدقي',
                    'bio': 'معلمة علوم متخصصة في المناهج الحديثة',
                    'specialization': 'العلوم',
                    'teaching_levels': 'preparatory,secondary',
                    'experience': 'خبرة 8 سنوات في تدريس العلوم',
                    'degree': 'phd',
                    'major': 'العلوم البيولوجية',
                    'certificates': 'دكتوراه في العلوم',
                    'payment_method': 'insta_pay',
                    'account_number': '01020000002',
                    'profit_percentage': 55,
                    'status': 'approved'
                }
            ]
            
            for teacher_data in teachers_data:
                Teacher.objects.create(**teacher_data)
            self.stdout.write('👨‍🏫 تم إنشاء 2 معلم عينة')
        
        # إنشاء كورسات عينة إذا لم تكن موجودة
        if not Course.objects.exists():
            teachers = Teacher.objects.all()
            if teachers.exists():
                courses_data = [
                    {
                        'title': 'رياضيات الصف الأول الثانوي',
                        'description': 'دورة شاملة في الرياضيات للصف الأول الثانوي',
                        'price': 500.00,
                        'teacher': teachers[0],
                        'subject': 'math',
                        'level': 'secondary',
                        'status': 'published'
                    },
                    {
                        'title': 'علوم الصف الثاني الإعدادي', 
                        'description': 'دورة متكاملة في العلوم للصف الثاني الإعدادي',
                        'price': 400.00,
                        'teacher': teachers[1],
                        'subject': 'science',
                        'level': 'preparatory',
                        'status': 'published'
                    }
                ]
                
                for course_data in courses_data:
                    Course.objects.create(**course_data)
                self.stdout.write('📚 تم إنشاء 2 كورس عينة')

    def create_sample_messages(self):
        """إنشاء رسائل تجريبية متنوعة"""
        
        try:
            admin = Admin.objects.first()
            students = Student.objects.all()
            teachers = Teacher.objects.filter(status='approved')
            courses = Course.objects.all()
            
            if not admin or not students.exists():
                self.stdout.write('⚠️ لا توجد بيانات كافية لإنشاء الرسائل')
                return

            # رسائل من الإدارة إلى الطلاب (جماعية وفردية)
            admin_messages = [
                {
                    'sender_type': 'admin',
                    'sender_id': admin.id,
                    'receiver_type': 'all_students',
                    'title': 'مرحباً بكم في منصة التعليم الذكي',
                    'content': 'نرحب بكم في منصتنا التعليمية. نتمنى لكم تجربة تعليمية ممتعة ومفيدة. يمكنكم التواصل معنا في أي وقت للحصول على المساعدة.'
                },
                {
                    'sender_type': 'admin', 
                    'sender_id': admin.id,
                    'receiver_type': 'all_students',
                    'title': 'بداية الفصل الدراسي الجديد',
                    'content': 'يسرنا إعلامكم ببداية الفصل الدراسي الجديد. نرجو متابعة الدروس بانتظام والاستفادة من المحتوى التعليمي المميز.'
                }
            ]

            for msg_data in admin_messages:
                Message.objects.create(
                    sender_type=msg_data['sender_type'],
                    sender_id=msg_data['sender_id'],
                    receiver_type=msg_data['receiver_type'],
                    title=msg_data['title'],
                    content=msg_data['content'],
                    expires_at=timezone.now() + timedelta(hours=48)
                )

            # رسائل فردية من الإدارة إلى طلاب محددين
            if students.exists():
                individual_messages = [
                    {
                        'title': 'رسالة ترحيب شخصية',
                        'content': 'مرحباً بك في المنصة. نحن هنا لمساعدتك في رحلتك التعليمية.'
                    },
                    {
                        'title': 'تنبيه مهم',
                        'content': 'نود تذكيرك بموعد الامتحان القادم. يرجى المراجعة الجيدة.'
                    }
                ]

                for i, student in enumerate(students[:2]):  # أول طالبين فقط
                    Message.objects.create(
                        sender_type='admin',
                        sender_id=admin.id,
                        receiver_type='student',
                        receiver_id=student.id,
                        title=individual_messages[i]['title'],
                        content=individual_messages[i]['content'],
                        expires_at=timezone.now() + timedelta(hours=48)
                    )

            # رسائل من المعلمين إلى طلاب الكورسات
            if teachers.exists() and courses.exists():
                teacher = teachers[0]
                course = courses[0]
                
                # الحصول على طلاب مسجلين في الكورس
                enrollments = Enrollment.objects.filter(course=course)
                if enrollments.exists():
                    Message.objects.create(
                        sender_type='teacher',
                        sender_id=teacher.id,
                        receiver_type='course_students',
                        course_id=course.id,
                        title='بداية كورس الرياضيات',
                        content='يسرني أن أعلن عن بداية كورس الرياضيات. نرجو متابعة الدروس بانتظام والمشاركة في الأنشطة.',
                        expires_at=timezone.now() + timedelta(hours=48)
                    )

            # رسائل من الطلاب إلى الإدارة
            if students.exists():
                student_messages = [
                    {
                        'title': 'استفسار عن الامتحانات',
                        'content': 'أود الاستفسار عن مواعيد الامتحانات النهائية للفصل الحالي.'
                    },
                    {
                        'title': 'مشكلة تقنية',
                        'content': 'أواجه مشكلة في تشغيل الفيديوهات التعليمية. يرجى المساعدة.'
                    }
                ]

                for i, student in enumerate(students[:2]):  # أول طالبين فقط
                    Message.objects.create(
                        sender_type='student',
                        sender_id=student.id,
                        receiver_type='admin',
                        receiver_id=admin.id,
                        title=student_messages[i]['title'],
                        content=student_messages[i]['content'],
                        expires_at=timezone.now() + timedelta(hours=48)
                    )

            # إنشاء بعض الإشعارات
            self.create_sample_notifications(students, teachers, admin)

            self.stdout.write(f'📨 تم إنشاء {Message.objects.count()} رسالة تجريبية')
            self.stdout.write(f'🔔 تم إنشاء {Notification.objects.count()} إشعار تجريبي')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ حدث خطأ في إنشاء البيانات: {str(e)}')
            )

    def create_sample_notifications(self, students, teachers, admin):
        """إنشاء إشعارات تجريبية"""
        
        try:
            # إشعارات للطلاب
            for student in students[:2]:  # أول طالبين فقط
                messages = Message.objects.filter(receiver_type='student', receiver_id=student.id)[:2]
                for message in messages:
                    Notification.objects.create(
                        user_type='student',
                        user_id=student.id,
                        message=message,
                        is_read=random.choice([True, False])
                    )

            # إشعارات للمعلمين
            for teacher in teachers:
                messages = Message.objects.filter(receiver_type='teacher', receiver_id=teacher.id)[:2]
                for message in messages:
                    Notification.objects.create(
                        user_type='teacher', 
                        user_id=teacher.id,
                        message=message,
                        is_read=random.choice([True, False])
                    )

            # إشعارات للإدارة
            admin_messages = Message.objects.filter(receiver_type='admin', receiver_id=admin.id)[:2]
            for message in admin_messages:
                Notification.objects.create(
                    user_type='admin',
                    user_id=admin.id, 
                    message=message,
                    is_read=random.choice([True, False])
                )

        except Exception as e:
            self.stdout.write(f'⚠️ خطأ في إنشاء الإشعارات: {e}')

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='مسح جميع البيانات الحالية قبل الإنشاء',
        )