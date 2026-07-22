from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import MenuItem
from .serializers import MenuItemSerializer


class MenuItemListCreateAPIView(generics.ListCreateAPIView):
    """GET: list all available menu items. POST: create a new one (requires login)."""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        restaurant = serializer.validated_data['restaurant']
        if restaurant.owner != self.request.user:
            raise PermissionDenied("You don't own this restaurant.")
        serializer.save()


class MenuItemDetailAPIView(generics.RetrieveDestroyAPIView):
    """GET: view a single menu item. DELETE: remove it (requires login + ownership)."""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_destroy(self, instance):
        if instance.restaurant.owner != self.request.user:
            raise PermissionDenied("You don't own this restaurant.")
        instance.delete()