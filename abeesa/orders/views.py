from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from restaurants.models import Restaurant
from .models import Order, OrderItem


@login_required
def place_order(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    menu_items = restaurant.menu_items.filter(is_available=True)
    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        order_items_to_create = []
        for item in menu_items:
            quantity_str = request.POST.get(f'quantity_{item.id}', '0')
            quantity = int(quantity_str) if quantity_str.isdigit() else 0
            if quantity > 0:
                order_items_to_create.append((item, quantity))
        if not delivery_address or not contact_phone:
            messages.error(request, "Please provide a delivery address and phone number.")
        elif not order_items_to_create:
            messages.error(request, "Pick at least one item before placing an order.")
        else:
            order = Order.objects.create(customer=request.user, restaurant=restaurant, delivery_address=delivery_address, contact_phone=contact_phone)
            for item, quantity in order_items_to_create:
                OrderItem.objects.create(order=order, menu_item=item, quantity=quantity, price_at_order_time=item.price)

            if request.user.email:
                send_mail(
                    subject="Order confirmation — " + restaurant.name,
                    message="Hi " + request.user.username + ",\n\nYour order #" + str(order.id) + " at " + restaurant.name + " has been placed successfully.\n\nDelivery address: " + delivery_address + "\nTotal: NGN " + str(order.total_price()) + "\n\nWe'll notify you when it's ready.\n\n— Abeesa",
                    from_email=None,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )

            if restaurant.owner.email:
                send_mail(
                    subject="New order received — Order #" + str(order.id),
                    message="Hi " + restaurant.owner.username + ",\n\nYou have a new order from " + request.user.username + " at " + restaurant.name + ".\n\nDelivery address: " + delivery_address + "\nPhone: " + contact_phone + "\nTotal: NGN " + str(order.total_price()) + "\n\nLog in to view and manage this order.\n\n— Abeesa",
                    from_email=None,
                    recipient_list=[restaurant.owner.email],
                    fail_silently=False,
                )

            messages.success(request, "Order placed at " + restaurant.name + "!")
            return redirect('my_orders')
    return render(request, 'orders/place_order.html', {'restaurant': restaurant, 'menu_items': menu_items})


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    if order.status in ['pending', 'confirmed']:
        if request.method == 'POST':
            order.status = 'cancelled'
            order.save()
            messages.success(request, "Order #" + str(order.id) + " was cancelled.")
        else:
            messages.error(request, 'Invalid request.')
    else:
        messages.error(request, "This order can no longer be cancelled.")
    return redirect('my_orders')


@login_required
def restaurant_orders(request, restaurant_pk):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    if restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')
    return render(request, 'orders/restaurant_orders.html', {'restaurant': restaurant, 'orders': orders})


@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, "Order #" + str(order.id) + " marked as " + order.get_status_display() + ".")

            if new_status == 'completed' and order.customer.email:
                send_mail(
                    subject="Your order is complete — " + order.restaurant.name,
                    message="Hi " + order.customer.username + ",\n\nYour order #" + str(order.id) + " at " + order.restaurant.name + " has been marked as completed.\n\nThanks for ordering with us!\n\n— Abeesa",
                    from_email=None,
                    recipient_list=[order.customer.email],
                    fail_silently=True,
                )

    return redirect('restaurant_orders', restaurant_pk=order.restaurant.pk)


@login_required
def mark_as_paid(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    if request.method == 'POST':
        order.payment_status = 'paid_pending_confirmation'
        order.save()
        messages.success(request, "Thanks! We've noted your payment claim — the restaurant will confirm it shortly.")
    return redirect('my_orders')


@login_required
def confirm_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.restaurant.owner != request.user:
        return HttpResponseForbidden("You don't own this restaurant.")
    if request.method == 'POST':
        order.payment_status = 'confirmed'
        order.save()
        messages.success(request, f"Payment confirmed for Order #{order.id}.")
    return redirect('restaurant_orders', restaurant_pk=order.restaurant.pk)