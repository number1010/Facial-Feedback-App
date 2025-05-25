from django.urls import path
from . import views

app_name = 'emotion_feedback'

urlpatterns = [
    path('', views.home, name='home'),
    path('capture/', views.EmotionCaptureView.as_view(), name='capture'),
    path('feedback/<str:session_id>/', views.FeedbackView.as_view(), name='feedback'),
    path('start-session/', views.start_session, name='start-session'),
    path('save-emotion/', views.save_emotion, name='save-emotion'),
    path('save-feedback/', views.save_feedback, name='save-feedback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank-you'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('view-feedback/<int:product_id>/', views.view_my_product_feedback, name='view_my_product_feedback'),
    path('delete-feedback/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('my-feedback/', views.my_feedback, name='my_feedback'),
] 