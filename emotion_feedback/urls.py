from django.urls import path
from . import views

app_name = 'emotion_feedback'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('capture/', views.EmotionCaptureView.as_view(), name='capture'),
    path('feedback/<str:session_id>/', views.FeedbackView.as_view(), name='feedback'),
    path('start-session/', views.start_session, name='start-session'),
    path('save-emotion/', views.save_emotion, name='save-emotion'),
    path('save-feedback/', views.save_feedback, name='save-feedback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank-you'),
] 