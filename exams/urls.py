from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('create/', views.create_exam, name='create_exam'),
    path('<int:exam_id>/questions/', views.exam_questions, name='exam_questions'),
    path('management/', views.exam_management, name='exam_management'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('student/', views.student_exams, name='student_exams'),
    path('<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('<int:exam_id>/result/', views.exam_result, name='exam_result'),
    path('api/wrong-answers/<int:exam_id>/<int:student_id>/', views.wrong_answers_api, name='wrong_answers_api'),
    path('<int:exam_id>/results/', views.exam_results_stats, name='exam_results_stats'),
    
]