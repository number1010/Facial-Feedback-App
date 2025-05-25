from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('select_topic/', views.select_topic, name='select_topic'),
    path('upload_product/<int:topic_id>/', views.upload_product, name='upload_product'),
    path('analyst_dashboard/', views.analyst_dashboard, name='analyst_dashboard'),
    path('product_management/', views.product_management, name='product_management'),
    path('product/<int:product_id>/feedback/', views.product_feedback, name='product_feedback'),
    path('product/<int:product_id>/view_feedback/', views.view_feedback, name='view_feedback'),
    path('product/<int:product_id>/stats/', views.product_stats, name='product_stats'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/add/', views.add_product, name='add_product'),
    path('feedback/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
] 