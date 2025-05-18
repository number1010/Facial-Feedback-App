from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('select-topic/', views.select_topic, name='select_topic'),
    path('upload-product/<int:topic_id>/', views.upload_product, name='upload_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('analyst-dashboard/', views.analyst_dashboard, name='analyst_dashboard'),
    path('product-feedback/<int:product_id>/', views.product_feedback, name='product_feedback'),
] 