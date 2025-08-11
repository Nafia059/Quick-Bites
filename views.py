# foodpanda/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden

from .models import (
    MenuItem, GroceryItem, Order, OrderItem, Restaurant,
    Review, HelpTicket, PromoCode, Notification, StaticPage,
    Referral, Rider, Delivery, Cart, CartItem, Address
)
from .forms import (
    MenuItemForm, GroceryItemForm, OrderForm, OrderItemForm,
    RestaurantForm, ReviewForm, HelpTicketForm, PromoCodeForm,
    NotificationForm, StaticPageForm, ReferralForm, RiderForm,
    DeliveryForm, CustomUserCreationForm, LoginForm,
    CartItemForm, CartForm, CheckoutForm
)

# -------------------- HOME --------------------
def home_view(request):
    return render(request, 'home.html')


# -------------------- MENU ITEM --------------------
@login_required
def menuitem_list(request):
    items = MenuItem.objects.filter(restaurant=request.user.restaurant)
    return render(request, 'menuitem_list.html', {'items': items})

@login_required
def menuitem_create(request):
    form = MenuItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.restaurant = request.user.restaurant
        item.save()
        return redirect('menuitem_list')
    return render(request, 'menuitem_form.html', {'form': form})

@login_required
def menuitem_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk, restaurant=request.user.restaurant)
    form = MenuItemForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('menuitem_list')
    return render(request, 'menuitem_form.html', {'form': form})

@login_required
def menuitem_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk, restaurant=request.user.restaurant)
    if request.method == 'POST':
        item.delete()
        return redirect('menuitem_list')
    return render(request, 'menuitem_confirm_delete.html', {'item': item})


# -------------------- GROCERY ITEM --------------------
@login_required
def groceryitem_list(request):
    items = GroceryItem.objects.filter(vendor=request.user.groceryvendor)
    return render(request, 'groceryitem_list.html', {'items': items})

@login_required
def groceryitem_create(request):
    form = GroceryItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.vendor = request.user.groceryvendor
        item.save()
        return redirect('groceryitem_list')
    return render(request, 'groceryitem_form.html', {'form': form})

@login_required
def groceryitem_update(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk, vendor=request.user.groceryvendor)
    form = GroceryItemForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('groceryitem_list')
    return render(request, 'groceryitem_form.html', {'form': form})

@login_required
def groceryitem_delete(request, pk):
    item = get_object_or_404(GroceryItem, pk=pk, vendor=request.user.groceryvendor)
    if request.method == 'POST':
        item.delete()
        return redirect('groceryitem_list')
    return render(request, 'groceryitem_confirm_delete.html', {'item': item})


# -------------------- RESTAURANT --------------------
@login_required
def restaurant_update(request):
    restaurant = get_object_or_404(Restaurant, user=request.user)
    form = RestaurantForm(request.POST or None, request.FILES or None, instance=restaurant)
    if form.is_valid():
        form.save()
        return redirect('restaurant_update')
    return render(request, 'restaurant_form.html', {'form': form})

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurant_list.html', {'restaurants': restaurants})

def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant_menu.html', {'restaurant': restaurant, 'menu_items': menu_items})


# -------------------- CART --------------------
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('menu_item', 'grocery_item')
    return render(request, 'cart.html', {'cart': cart, 'items': items})

@login_required
def add_to_cart(request, item_type, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if item_type == 'food':
        item = get_object_or_404(MenuItem, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, item_type='food', menu_item=item, defaults={'quantity': 1})
    elif item_type == 'grocery':
        item = get_object_or_404(GroceryItem, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, item_type='grocery', grocery_item=item, defaults={'quantity': 1})
    else:
        return redirect('home')
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')

@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_view')

@login_required
@require_POST
def update_cart_item_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        qty = int(request.POST.get('quantity', 1))
        if qty >= 1:
            item.quantity = qty
            item.save()
            messages.success(request, "Quantity updated.")
        else:
            messages.error(request, "Quantity must be at least 1.")
    except ValueError:
        messages.error(request, "Invalid quantity.")
    return redirect('cart_view')


# -------------------- CHECKOUT --------------------
@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('menu_item', 'grocery_item')
    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_view')

    if request.method == 'POST':
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address') or Address.objects.create(
                user=request.user,
                address_text=form.cleaned_data['address_text'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude')
            )

            total_amount = sum([
                item.menu_item.price * item.quantity if item.item_type == 'food'
                else item.grocery_item.price * item.quantity for item in items
            ])
            # Determine delivery fee
            restaurant = items[0].menu_item.restaurant if items[0].item_type == 'food' else None
            delivery_fee = 0

# Free delivery if it's the user's first order
            is_first_order = not Order.objects.filter(user=request.user).exists()

            if not is_first_order and restaurant:
             delivery_fee = restaurant.delivery_fee

# Calculate total
            total_amount = sum([
            item.menu_item.price * item.quantity if item.item_type == 'food'
            else item.grocery_item.price * item.quantity for item in items
            ]) + delivery_fee


            order = Order.objects.create(
                user=request.user,
                delivery_address=address,
                payment_method=form.cleaned_data['payment_method'],
                status='Pending' if form.cleaned_data['payment_method'] == 'Card' else 'Placed',
                total_amount=total_amount
            )

            for cart_item in items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item if cart_item.item_type == 'food' else None,
                    grocery_item=cart_item.grocery_item if cart_item.item_type == 'grocery' else None,
                    quantity=cart_item.quantity,
                    price=(cart_item.menu_item or cart_item.grocery_item).price
                )

            # 🚚 Create Delivery and assign a rider
            rider = Rider.objects.order_by('?').first()
            if rider:
                Delivery.objects.create(
                    rider=rider,
                    order=order,
                    status='Pending'
                )
            else:
                messages.warning(request, "Order placed, but no rider available yet. It will be assigned soon.")

            cart.items.all().delete()
            request.session['last_address_id'] = None


            send_mail(
                'Order Confirmation',
                f'Hi {request.user.username},\n\nYour order has been placed successfully. Thank you for choosing Foodpanda Clone!',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=True
            )

            messages.success(request, "Order placed successfully. Confirmation email sent.")
            if order.payment_method == 'Card':
                return redirect(reverse('card_payment', args=[order.id]))
            return redirect('order_list')
    else:
        last_address_id = request.session.get('last_address_id')
    if last_address_id:
        try:
            address = Address.objects.get(id=last_address_id, user=request.user)
            form = CheckoutForm(request.user, initial={
                'address_text': address.address_text,
                'city': address.city,
                'postal_code': address.postal_code,
                'latitude': address.latitude,
                'longitude': address.longitude,
            })
        except Address.DoesNotExist:
            form = CheckoutForm(request.user)
    else:
        form = CheckoutForm(request.user)


    return render(request, 'checkout.html', {'cart': cart, 'items': items, 'form': form})

@login_required
def customer_orders(request):
    if request.user.user_type != 'customer':
        return redirect('home')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})


# -------------------- CARD PAYMENT --------------------
@login_required
def card_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'Pending' or order.payment_method != 'Card':
        messages.error(request, "Invalid payment attempt.")
        return redirect('order_list')

    if request.method == 'POST':
        order.status = 'Placed'
        order.save()
        send_mail(
            'Payment Confirmed',
            f'Hi {request.user.username},\n\nYour payment for order #{order.id} is confirmed!',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=True
        )
        messages.success(request, "Payment successful & email sent!")
        return redirect('order_list')
    return render(request, 'card_payment.html', {'order': order})


# -------------------- ORDER --------------------
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__menu_item', 'items__grocery_item')
    return render(request, 'order_list.html', {'orders': orders})

@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    form = OrderForm(request.POST or None, instance=order)
    if form.is_valid():
        form.save()
        return redirect('order_list')
    return render(request, 'order_form.html', {'form': form})

@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')
    return render(request, 'order_confirm_delete.html', {'order': order})


# -------------------- REVIEW --------------------
@login_required
def review_create(request):
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.save()
        return redirect('order_list')
    return render(request, 'review_form.html', {'form': form})


# -------------------- HELP TICKET --------------------
@login_required
def helpticket_list(request):
    tickets = HelpTicket.objects.filter(user=request.user)
    return render(request, 'helpticket_list.html', {'tickets': tickets})

@login_required
def helpticket_create(request):
    form = HelpTicketForm(request.POST or None)
    if form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()
        return redirect('helpticket_list')
    return render(request, 'helpticket_form.html', {'form': form})


# -------------------- PROMO CODE --------------------
@login_required
def promocode_list(request):
    codes = PromoCode.objects.all()
    return render(request, 'promocode_list.html', {'codes': codes})

@login_required
def promocode_create(request):
    form = PromoCodeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('promocode_list')
    return render(request, 'promocode_form.html', {'form': form})


# -------------------- NOTIFICATIONS --------------------
@login_required
def notification_list(request):
    notes = Notification.objects.filter(user=request.user)
    return render(request, 'notification_list.html', {'notifications': notes})


# -------------------- STATIC PAGES --------------------
@login_required
def staticpage_update(request, pk):
    page = get_object_or_404(StaticPage, pk=pk)
    form = StaticPageForm(request.POST or None, instance=page)
    if form.is_valid():
        form.save()
        return redirect('staticpage_update', pk=pk)
    return render(request, 'staticpage_form.html', {'form': form})


# -------------------- REFERRALS --------------------
@login_required
def referral_list(request):
    refs = Referral.objects.filter(user=request.user)
    return render(request, 'referral_list.html', {'referrals': refs})


# -------------------- RIDER --------------------
@login_required
def rider_update(request):
    rider = get_object_or_404(Rider, user=request.user)
    form = RiderForm(request.POST or None, instance=rider)
    if form.is_valid():
        form.save()
        return redirect('rider_update')
    return render(request, 'rider_form.html', {'form': form})


# -------------------- DELIVERY --------------------
@login_required
def delivery_update(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    form = DeliveryForm(request.POST or None, instance=delivery)
    if form.is_valid():
        form.save()
        return redirect('order_list')
    return render(request, 'delivery_form.html', {'form': form})


# -------------------- AUTH --------------------
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

from .models import Rider

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on user_type
            if user.user_type == 'restaurant':
                return redirect('restaurant_dashboard')
            elif user.user_type == 'rider':
                # ✅ Auto-create rider profile if not exist
                Rider.objects.get_or_create(user=user)
                return redirect('rider_dashboard')
            elif user.user_type == 'grocery_vendor':
                return redirect('grocery_dashboard')  # if you have this
            else:
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('home')


# -------------------- RESTAURANT DASHBOARD --------------------
from .models import Delivery

@login_required
def restaurant_dashboard(request):
    restaurant = Restaurant.objects.filter(user=request.user).first()
    if not restaurant:
        return render(request, 'restaurant/no_restaurant.html')

    order_items = OrderItem.objects.filter(
        menu_item__restaurant=restaurant
    ).select_related('order', 'menu_item')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        if order_id and new_status:
            try:
                order = Order.objects.get(id=order_id)
                order.status = new_status
                order.save()

                # ✅ Automatically create Delivery if status is "on the way"
                if new_status.lower() == "on the way":
                    # Check if delivery already exists to avoid duplication
                    Delivery.objects.get_or_create(order=order)

            except Order.DoesNotExist:
                messages.error(request, "Order not found.")

    deliveries = Delivery.objects.filter(order__in=[oi.order for oi in order_items])

    return render(request, 'restaurant/dashboard.html', {
        'restaurant': restaurant,
        'order_items': order_items,
        'deliveries': deliveries,
    })


# views.py
from django.http import HttpResponseForbidden

from django.utils import timezone
from .models import Rider, Delivery, Order

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not hasattr(request.user, 'restaurant'):
        return HttpResponseForbidden("You are not a restaurant user.")

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            order.status = new_status
            order.save()

            # ✅ Create Delivery if status is "On the way" and no delivery exists yet
            delivery_exists = Delivery.objects.filter(order=order).exists()
            if new_status == 'On the way' and not delivery_exists:
                available_rider = Rider.objects.filter(is_available=True).first()
                if available_rider:
                    Delivery.objects.create(
                        order=order,
                        rider=available_rider,
                        status='Pending',
                    )
                    available_rider.is_available = False
                    available_rider.save()

        return redirect('restaurant_dashboard')

    return render(request, 'restaurant/update_order_status.html', {'order': order})


@login_required
def orderitem_create(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Optional: Only allow if this user owns the order or is a restaurant admin
    if request.user != order.user and request.user.user_type != 'restaurant':
        return HttpResponseForbidden("You are not allowed to add items to this order.")

    form = OrderItemForm(request.POST or None)
    if form.is_valid():
        order_item = form.save(commit=False)
        order_item.order = order
        order_item.save()
        messages.success(request, "Item added to order.")
        return redirect('order_list')
    return render(request, 'orderitem_form.html', {'form': form, 'order': order})
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Delivery
from foodpanda.models import Notification, Order  # adjust if in different app


from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Delivery, Notification

@login_required
def rider_dashboard(request):
    try:
        rider = request.user.rider
    except AttributeError:
        return render(request, 'rider/no_rider_profile.html')

    selected_status = request.GET.get('status')
    if selected_status:
        deliveries = Delivery.objects.filter(rider=rider, status=selected_status)
    else:
        deliveries = Delivery.objects.filter(rider=rider)

    if request.method == 'POST':
        delivery_id = request.POST.get('delivery_id')
        new_status = request.POST.get(f'status_{delivery_id}')

        if delivery_id and new_status:
            try:
                delivery = Delivery.objects.get(id=delivery_id, rider=rider)

                if new_status in dict(Delivery.DELIVERY_STATUS_CHOICES):
                    delivery.status = new_status

                    if new_status == 'Picked up' and not delivery.pickup_time:
                        delivery.pickup_time = timezone.now()
                    elif new_status == 'Delivered' and not delivery.delivery_time:
                        delivery.delivery_time = timezone.now()

                    delivery.save()

                    # Update the related order status
                    order = delivery.order
                    if new_status == 'Delivered':
                        order.status = 'Delivered'
                    elif new_status == 'Cancelled':
                        order.status = 'Cancelled'
                    order.save()

                    # Notify customer
                    if hasattr(order, 'customer') and order.customer.user:
                        Notification.objects.create(
                            user=order.customer.user,
                            message=f"Order #{order.short_code} has been marked as {new_status.lower()} by the rider."
                        )

                    # Notify restaurant
                    if hasattr(order, 'restaurant') and order.restaurant.user:
                        Notification.objects.create(
                            user=order.restaurant.user,
                            message=f"Order #{order.short_code} has been marked as {new_status.lower()} by the rider."
                        )

            except Delivery.DoesNotExist:
                pass

        return redirect('rider_dashboard')

    return render(request, 'rider/dashboard.html', {
        'deliveries': deliveries,
        'selected_status': selected_status,
        'status_choices': Delivery.DELIVERY_STATUS_CHOICES,
    })







from django.core.mail import send_mail
from django.conf import settings
from .models import Notification  # if you have it

@login_required
def update_delivery_status(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)

    if request.user != delivery.rider.user:
        return redirect('rider_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Delivery.DELIVERY_STATUS_CHOICES):
            delivery.status = new_status

            if new_status == 'Picked up' and not delivery.pickup_time:
                delivery.pickup_time = timezone.now()

            elif new_status == 'Delivered' and not delivery.delivery_time:
                delivery.delivery_time = timezone.now()
                delivery.order.status = 'Delivered'
                delivery.order.save()

                # Mark rider available again
                delivery.rider.is_available = True
                delivery.rider.save()

                # ✅ Send email to customer
                send_mail(
                    'Your order has been delivered!',
                    f"Hi {delivery.order.user.username},\n\nYour order #{delivery.order.id} has been successfully delivered. Thank you!",
                    settings.DEFAULT_FROM_EMAIL,
                    [delivery.order.user.email],
                    fail_silently=True,
                )

                # ✅ Optional in-app notification
                Notification.objects.create(
                    user=delivery.order.user,
                    message=f"Your order #{delivery.order.id} has been delivered!"
                )

            elif new_status == 'Cancelled':
                delivery.order.status = 'Cancelled'
                delivery.order.save()

                delivery.rider.is_available = True
                delivery.rider.save()

                # ✅ Email for cancellation
                send_mail(
                    'Your order has been cancelled',
                    f"Hi {delivery.order.user.username},\n\nUnfortunately, your order #{delivery.order.id} has been cancelled. Contact support for help.",
                    settings.DEFAULT_FROM_EMAIL,
                    [delivery.order.user.email],
                    fail_silently=True,
                )

                Notification.objects.create(
                    user=delivery.order.user,
                    message=f"Your order #{delivery.order.id} has been cancelled."
                )

            delivery.save()

    return redirect('rider_dashboard')
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

@csrf_exempt
@login_required
def save_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        address = Address.objects.create(
            user=request.user,
            address_text=data['address_text'],
            city=data.get('city', ''),
            postal_code=data.get('postal_code', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        request.session['last_address_id'] = address.id
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
