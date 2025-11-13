from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.views import home  # تأكد من استيراد دالة home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # الصفحة الرئيسية
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('courses/', include('courses.urls')),
    path('enrollments/', include('enrollments.urls')),
    path('ratings/', include('ratings.urls')),
    path('reports/', include('reports.urls')),
    path('messaging/', include('messaging.urls')),
    path('admins/', include('admins.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)