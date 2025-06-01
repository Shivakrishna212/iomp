from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user-login/', views.user_login, name='user_login'),
    path('user-register/', views.user_register, name='user_register'),
    path('user-contact/', views.user_contact, name='user_contact'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user-questions/<str:subject>/', views.user_questions, name='user_questions'),
    path('user-view-results/<int:answer_id>/', views.user_view_results, name='user_view_results'),
    path('user-results/', views.user_results, name='user_results'),
    path('user-myprofile/', views.user_myprofile, name='user_myprofile'),
    path('user-exam/', views.user_exam, name='user_exam'),
    path('upload-answer/', views.upload_answer, name='upload_answer'),
    path('upload-answer-sheet/', views.upload_answer_sheet, name='upload_answer_sheet'),
    path('get-questions/<int:exam_id>/', views.get_questions, name='get_questions'),
    path('api/compare-texts/', views.compare_texts_api, name='compare_texts_api'),
    path('get-questions-by-subject/<str:subject>/', views.get_questions_by_subject, name='get_questions_by_subject'),
] 