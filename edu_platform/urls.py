# edu_platform/urls.py - الملف الرئيسي الكامل
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView  # أضف هذا السطر

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # تطبيقات المشروع
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('courses/', include('courses.urls')),
    path('admins/', include('admins.urls')),
    path('enrollments/', include('enrollments.urls')),
    path('ratings/', include('ratings.urls')),
    path('reports/', include('reports.urls')),
    path('messaging/', include('messaging.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)