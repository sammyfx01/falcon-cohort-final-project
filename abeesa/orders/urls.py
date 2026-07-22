from django.urls import path
from . import views
from .api_views import OrderListCreateAPIView, OrderDetailAPIView

urlpatterns = [
    path('restaurants/<int:restaurant_pk>/order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('orders/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('restaurants/<int:restaurant_pk>/orders/', views.restaurant_orders, name='restaurant_orders'),
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:pk>/mark-paid/', views.mark_as_paid, name='mark_as_paid'),
    path('orders/<int:pk>/confirm-payment/', views.confirm_payment, name='confirm_payment'),

    # REST API
    path('api/orders/', OrderListCreateAPIView.as_view(), name='api_order_list'),
    path('api/orders/<int:pk>/', OrderDetailAPIView.as_view(), name='api_order_detail'),
]