from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/rate/', views.submit_course_rating, name='submit_course_rating'),
    path('course/<int:course_id>/ratings/', views.get_course_ratings, name='get_course_ratings'),
    path('teacher/<int:teacher_id>/rate/', views.submit_teacher_rating, name='submit_teacher_rating'),
    path('teacher/<int:teacher_id>/ratings/', views.get_teacher_ratings, name='get_teacher_ratings'),
]