from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('register/', views.register, name='register'),
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
]