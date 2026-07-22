from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer


class OrderListCreateAPIView(generics.ListCreateAPIView):
    """GET: list the logged-in user's own orders. POST: create a new order."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class OrderDetailAPIView(generics.RetrieveDestroyAPIView):
    """GET: view a single order. DELETE: cancel/remove it (owner only)."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)