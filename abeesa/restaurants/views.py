from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Restaurant, MenuItem


def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.all()
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})