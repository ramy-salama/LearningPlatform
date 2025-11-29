from django.shortcuts import render
from django.http import HttpResponse
from .models import Course

def home(request):
    # جلب الكورسات المنشورة
    courses = Course.objects.filter(status='published').order_by('-students_count', '-created_at')[:6]
    
    # بناء HTML بالكورسات
    courses_html = ""
    for course in courses:
        courses_html += f"""
        <div class="course-card">
            <h3>{course.title}</h3>
            <p>المعلم: {course.teacher}</p>
            <p>عدد الطلاب: {course.students_count}</p>
            <p>السعر: {course.price} جنيه</p>
            <p>التقييم: {course.average_rating} ⭐</p>
        </div>
        """
    
    if not courses:
        courses_html = "<p>لا توجد كورسات متاحة حالياً</p>"

    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title> درس أونلاين </title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                color: white;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 60px 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                margin-bottom: 40px;
                backdrop-filter: blur(10px);
            }}
            h1 {{
                font-size: 2.5em;
                margin-bottom: 20px;
            }}
            .courses-section {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            .courses-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .course-card {{
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .course-card h3 {{
                margin-top: 0;
                color: #fff;
            }}
            .links {{
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 30px;
            }}
            .btn {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 12px 25px;
                text-decoration: none;
                border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: all 0.3s ease;
                font-weight: bold;
            }}
            .btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 منصة التعليم الذكي</h1>
                <p>مرحباً بك في نظام إدارة المنصة التعليمية</p>
                <div class="links">
                    <a href="/admin/" class="btn">لوحة الإدارة</a>
                    <a href="/students/login/" class="btn">تسجيل دخول الطالب</a>
                    <a href="/teachers/login/" class="btn">تسجيل دخول المعلم</a>
                </div>
            </div>
            
            <div class="courses-section">
                <h2>🎯 الكورسات المتاحة ({courses.count()})</h2>
                <div class="courses-grid">
                    {courses_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """)