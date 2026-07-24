from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Restaurant, MenuItem, ContactMessage, Review
from .forms import MenuItemForm, ContactForm, ReviewForm


def restaurant_list(request):
    query = request.GET.get('q', '').strip()
    restaurants = Restaurant.objects.all()
    search_results = None

    if query:
        search_results = MenuItem.objects.filter(name__icontains=query, is_available=True)
    else:
        featured_items = MenuItem.objects.filter(is_available=True).order_by('-id')[:6]

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants,
        'featured_items': featured_items if not query else None,
        'search_results': search_results,
        'query': query,
    })


def menu_item_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    is_owner = request.user.is_authenticated and item.restaurant.owner == request.user
    reviews = item.reviews.all().order_by('-created_at')

    existing_review = None
    if request.user.is_authenticated:
        existing_review = Review.objects.filter(menu_item=item, customer=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.menu_item = item
            review.customer = request.user
            review.save()
            messages.success(request, "Thanks for your review!")
            return redirect('menu_item_detail', pk=item.pk)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'restaurants/menu_item_detail.html', {
        'item': item,
        'is_owner': is_owner,
        'reviews': reviews,
        'form': form,
        'existing_review': existing_review,
    })
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.all()
    is_owner = request.user.is_authenticated and restaurant.owner == request.user
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'is_owner': is_owner,
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


@login_required
def menu_item_create(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    if restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            messages.success(request, f'"{item.name}" was added to the menu.')
            return redirect('restaurant_detail', pk=restaurant.pk)
    else:
        form = MenuItemForm()
    return render(request, 'restaurants/menu_item_form.html', {'form': form, 'action': 'Add', 'restaurant': restaurant})


@login_required
def menu_item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if item.restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{item.name}" was updated.')
            return redirect('restaurant_detail', pk=item.restaurant.pk)
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'restaurants/menu_item_form.html', {'form': form, 'action': 'Edit'})


@login_required
def menu_item_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if item.restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    restaurant_pk = item.restaurant.pk
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'"{item_name}" was removed from the menu.')
        return redirect('restaurant_detail', pk=restaurant_pk)
    return render(request, 'restaurants/menu_item_confirm_delete.html', {'item': item})


@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'restaurants/contact.html', {'form': form})


@login_required
def restaurant_contact(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.restaurant = restaurant
            msg.sender = request.user
            msg.save()
            messages.success(request, f"Your message was sent to {restaurant.name}.")
            return redirect('restaurant_detail', pk=restaurant.pk)
    else:
        form = ContactForm()
    return render(request, 'restaurants/restaurant_contact.html', {'form': form, 'restaurant': restaurant})


@login_required
def restaurant_messages(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    if restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    inbox = restaurant.messages.all().order_by('-created_at')
    return render(request, 'restaurants/restaurant_messages.html', {'restaurant': restaurant, 'inbox': inbox})


@login_required
def reply_to_message(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.restaurant or msg.restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    if request.method == 'POST':
        msg.response = "Thanks for reaching out — we've seen your message and will follow up with you shortly."
        msg.is_read = True
        msg.responded_at = timezone.now()
        msg.save()
        messages.success(request, "Reply sent.")
    return redirect('restaurant_messages', restaurant_pk=msg.restaurant.pk)


@login_required
def my_messages(request):
    sent = ContactMessage.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'restaurants/my_messages.html', {'sent': sent})