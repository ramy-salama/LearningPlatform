# messaging/management/commands/cleanup_expired_messages.py
from django.core.management.base import BaseCommand
from messaging.models import Message, Notification
from django.utils import timezone
from datetime import timedelta
import logging

# إعداد logger للأفضل
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'تنظيف الرسائل والإشعارات المنتهية الصلاحية'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض ما سيتم حذفه دون تنفيذ الحذف الفعلي',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=2,
            help='عدد الأيام للاحتفاظ بالرسائل (افتراضي: 2 يوم)',
        )
        parser.add_argument(
            '--include-read',
            action='store_true', 
            help='حذف الرسائل المقروءة أيضاً التي انتهت صلاحيتها',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_old = options['days']
        include_read = options['include_read']
        
        self.stdout.write('🔍 بدء عملية تنظيف الرسائل المنتهية...')
        
        try:
            # حساب تاريخ انتهاء الصلاحية
            expiry_date = timezone.now() - timedelta(days=days_old)
            
            self.stdout.write(f'📅 البحث عن الرسائل الأقدم من: {expiry_date.strftime("%Y-%m-%d %H:%M")}')
            
            # البحث عن الرسائل المنتهية
            expired_messages_query = Message.objects.filter(
                expires_at__lt=timezone.now()
            )
            
            if not include_read:
                expired_messages_query = expired_messages_query.filter(is_read=True)
            
            expired_messages = expired_messages_query
            expired_count = expired_messages.count()
            
            # البحث عن الإشعارات المرتبطة
            expired_notifications = Notification.objects.filter(
                message__in=expired_messages
            )
            expired_notifications_count = expired_notifications.count()
            
            # عرض النتائج
            self.stdout.write(f'📨 عدد الرسائل المنتهية: {expired_count}')
            self.stdout.write(f'🔔 عدد الإشعارات المنتهية: {expired_notifications_count}')
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('🔶 وضع التجربة - لم يتم حذف أي بيانات')
                )
                
                # عرض عينة من الرسائل التي سيتم حذفها
                if expired_count > 0:
                    self.stdout.write('\n📋 عينة من الرسائل التي سيتم حذفها:')
                    sample_messages = expired_messages[:5]
                    for msg in sample_messages:
                        self.stdout.write(
                            f'   - {msg.title} (من: {msg.get_sender_name()}, إلى: {msg.receiver_type})'
                        )
                    
                    if expired_count > 5:
                        self.stdout.write(f'   ... و {expired_count - 5} رسالة أخرى')
                
                return
            
            # التنفيذ الفعلي للحذف
            if expired_count > 0:
                self.stdout.write('🗑️ بدء حذف البيانات المنتهية...')
                
                # تسجيل المعلومات قبل الحذف للأرشفة
                self.log_deletion_info(expired_messages)
                
                # حذف الإشعارات أولاً (بسبب العلاقات)
                notifications_deleted, _ = expired_notifications.delete()
                
                # ثم حذف الرسائل
                messages_deleted, deleted_dict = expired_messages.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ تم الانتهاء من التنظيف:\n'
                        f'   • تم حذف {messages_deleted} رسالة\n'
                        f'   • تم حذف {notifications_deleted} إشعار'
                    )
                )
                
                # تسجيل العملية
                logger.info(
                    f'Cleanup completed: {messages_deleted} messages, '
                    f'{notifications_deleted} notifications deleted'
                )
                
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ لا توجد رسائل منتهية الصلاحية للحذف')
                )
                
        except Exception as e:
            error_msg = f'❌ حدث خطأ أثناء عملية التنظيف: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg)
            raise

    def log_deletion_info(self, messages_queryset):
        """تسجيل معلومات عن الرسائل التي سيتم حذفها للأرشفة"""
        
        try:
            # إحصائيات عن الرسائل التي سيتم حذفها
            stats = {
                'total': messages_queryset.count(),
                'by_sender_type': {},
                'by_receiver_type': {},
                'read_vs_unread': {
                    'read': messages_queryset.filter(is_read=True).count(),
                    'unread': messages_queryset.filter(is_read=False).count()
                }
            }
            
            # إحصائيات حسب نوع المرسل
            for sender_type in ['admin', 'teacher', 'student']:
                count = messages_queryset.filter(sender_type=sender_type).count()
                if count > 0:
                    stats['by_sender_type'][sender_type] = count
            
            # إحصائيات حسب نوع المستقبل
            for receiver_type in ['admin', 'teacher', 'student', 'all_students', 'course_students']:
                count = messages_queryset.filter(receiver_type=receiver_type).count()
                if count > 0:
                    stats['by_receiver_type'][receiver_type] = count
            
            # تسجيل الإحصائيات
            logger.info(f'Cleanup statistics: {stats}')
            
            self.stdout.write('📊 إحصائيات البيانات التي تم حذفها:')
            self.stdout.write(f'   • الإجمالي: {stats["total"]} رسالة')
            self.stdout.write(f'   • المقروءة: {stats["read_vs_unread"]["read"]}')
            self.stdout.write(f'   • غير المقروءة: {stats["read_vs_unread"]["unread"]}')
            
            if stats['by_sender_type']:
                self.stdout.write('   • حسب المرسل:')
                for sender, count in stats['by_sender_type'].items():
                    self.stdout.write(f'     - {sender}: {count}')
                    
            if stats['by_receiver_type']:
                self.stdout.write('   • حسب المستقبل:')
                for receiver, count in stats['by_receiver_type'].items():
                    self.stdout.write(f'     - {receiver}: {count}')
                    
        except Exception as e:
            logger.warning(f'Failed to log deletion stats: {e}')

# أمر إضافي للصيانة الدورية
class CommandExtended(Command):
    """إصدار موسع مع خيارات صيانة إضافية"""
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--clean-orphaned',
            action='store_true',
            help='حذف الإشعارات اليتيمة (بدون رسائل)',
        )
        parser.add_argument(
            '--fix-expiry',
            action='store_true', 
            help='إصلاح تواريخ انتهاء الصلاحية المفقودة',
        )

    def handle(self, *args, **options):
        # التنظيف الأساسي
        super().handle(*args, **options)
        
        # مهام صيانة إضافية
        if options['clean_orphaned']:
            self.clean_orphaned_notifications(options['dry_run'])
            
        if options['fix_expiry']:
            self.fix_missing_expiry_dates(options['dry_run'])

    def clean_orphaned_notifications(self, dry_run=False):
        """تنظيف الإشعارات اليتيمة"""
        
        try:
            # الإشعارات التي لا ترتبط بأي رسالة
            orphaned_notifications = Notification.objects.filter(message__isnull=True)
            orphaned_count = orphaned_notifications.count()
            
            self.stdout.write(f'🔍 عدد الإشعارات اليتيمة: {orphaned_count}')
            
            if dry_run:
                if orphaned_count > 0:
                    self.stdout.write('🔶 (وضع التجربة) سيتم حذف الإشعارات اليتيمة')
                return
                
            if orphaned_count > 0:
                deleted_count, _ = orphaned_notifications.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ تم حذف {deleted_count} إشعار يتيم')
                )
                logger.info(f'Deleted {deleted_count} orphaned notifications')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في تنظيف الإشعارات اليتيمة: {e}'))

    def fix_missing_expiry_dates(self, dry_run=False):
        """إصلاح الرسائل التي تفتقد تواريخ انتهاء الصلاحية"""
        
        try:
            from datetime import timedelta
            
            # الرسائل التي تفتقد تاريخ انتهاء الصلاحية
            messages_without_expiry = Message.objects.filter(expires_at__isnull=True)
            fix_count = messages_without_expiry.count()
            
            self.stdout.write(f'🔧 عدد الرسائل التي تحتاج إصلاح: {fix_count}')
            
            if dry_run:
                if fix_count > 0:
                    self.stdout.write('🔶 (وضع التجربة) سيتم إصلاح تواريخ الانتهاء')
                return
                
            if fix_count > 0:
                updated_count = 0
                for message in messages_without_expiry:
                    # تعيين تاريخ انتهاء افتراضي (48 ساعة من الإنشاء)
                    if message.created_at:
                        message.expires_at = message.created_at + timedelta(hours=48)
                    else:
                        message.expires_at = timezone.now() + timedelta(hours=48)
                    message.save()
                    updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ تم إصلاح {updated_count} رسالة')
                )
                logger.info(f'Fixed expiry dates for {updated_count} messages')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في إصلاح التواريخ: {e}'))