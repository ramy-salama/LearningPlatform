from django import template
from exams.models import Exam
from django.utils import timezone

register = template.Library()

@register.filter
def has_active_exams(course):
    """التحقق إذا كان الكورس له اختبارات نشطة"""
    now = timezone.now()
    return Exam.objects.filter(
        course=course,
        is_active=True,
        question_set__count__gte=10,
        start_date__lte=now,
        end_date__gte=now
    ).exists()