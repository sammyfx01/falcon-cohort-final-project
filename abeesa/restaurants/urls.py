from django.urls import path
from . import views
from .api_views import MenuItemListCreateAPIView, MenuItemDetailAPIView

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('register/', views.register, name='register'),
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_pk>/menu-items/create/', views.menu_item_create, name='menu_item_create'),
    path('menu-items/<int:pk>/edit/', views.menu_item_update, name='menu_item_update'),
    path('menu-items/<int:pk>/delete/', views.menu_item_delete, name='menu_item_delete'),
    path('contact/', views.contact, name='contact'),
    path('restaurants/<int:restaurant_pk>/contact/', views.restaurant_contact, name='restaurant_contact'),
    path('restaurants/<int:restaurant_pk>/messages/', views.restaurant_messages, name='restaurant_messages'),
    path('messages/<int:pk>/reply/', views.reply_to_message, name='reply_to_message'),
    path('my-messages/', views.my_messages, name='my_messages'),

    # REST API
    path('api/menu-items/', MenuItemListCreateAPIView.as_view(), name='api_menu_item_list'),
    path('api/menu-items/<int:pk>/', MenuItemDetailAPIView.as_view(), name='api_menu_item_detail'),
]