from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils.crypto import get_random_string
# -------------------- USERS --------------------

class User(AbstractUser):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('restaurant', 'Restaurant'),
        ('grocery_vendor', 'Grocery Vendor'),
        ('rider', 'Rider'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)

    def __str__(self):
        return self.username

# -------------------- ADDRESSES --------------------

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=100)
    address_text = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.label} - {self.city}"

# -------------------- RESTAURANTS --------------------

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'restaurant'})
    cover_photo = models.ImageField(upload_to='restaurant_covers/', blank=True, null=True)
    food_type = models.CharField(max_length=100, help_text="e.g. Chinese, Fast Food, Desi, Italian", default="General")
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_delivery_time = models.DurationField(help_text="e.g., 00:45:00", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Restaurant"

class GroceryVendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'grocery_vendor'})
    store_name = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name

# -------------------- CATEGORIES --------------------

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# -------------------- MENU ITEMS --------------------

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class GroceryItem(models.Model):
    vendor = models.ForeignKey(GroceryVendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='grocery_items/')

    def __str__(self):
        return self.name

# -------------------- CART --------------------

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('food', 'Food'),
        ('grocery', 'Grocery'),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', null=True, blank=True)  # nullable for migration safety
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    grocery_item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        if self.item_type == 'food' and self.menu_item:
            return self.menu_item.price * self.quantity
        elif self.item_type == 'grocery' and self.grocery_item:
            return self.grocery_item.price * self.quantity
        return 0

    def __str__(self):
        return f"{self.quantity} x {self.menu_item or self.grocery_item}"

# -------------------- ORDERS --------------------
import random
import string

def generate_short_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Placed', 'Placed'),
        ('Preparing', 'Preparing'),
        ('On the way', 'On the way'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('Card', 'Card Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD')
    status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='Placed')
    created_at = models.DateTimeField(auto_now_add=True)

    short_code = models.CharField(max_length=10, blank=True, null=True)  # ← no unique yet


    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = get_random_string(8).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.short_code} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    grocery_item = models.ForeignKey(GroceryItem, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item or self.grocery_item}"

# -------------------- PAYMENT --------------------

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"

# -------------------- DELIVERY --------------------

class Rider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'rider'})
    is_available = models.BooleanField(default=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Rider {self.user.username}"

class Delivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Picked up', 'Picked up'),
        ('Delivered', 'Delivered'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, choices=DELIVERY_STATUS_CHOICES, default='Pending')
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order {self.order.id}"

# -------------------- REVIEWS --------------------

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    grocery_vendor = models.ForeignKey(GroceryVendor, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username}"

# -------------------- SUPPORT --------------------

class HelpTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HelpTicket: {self.subject}"

# -------------------- PROMO --------------------

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()
    expiry_date = models.DateField()
    usage_limit = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

# -------------------- NOTIFICATIONS --------------------

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"

# -------------------- STATIC PAGES --------------------

class StaticPage(models.Model):
    PAGE_CHOICES = [
        ('terms', 'Terms of Use'),
        ('privacy', 'Privacy Policy'),
        ('refund', 'Refund Policy'),
    ]

    page_type = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.page_type

# -------------------- REFERRALS --------------------

class Referral(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    referred_email = models.EmailField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'referred_email')

    def __str__(self):
        return f"{self.user.username} referred {self.referred_email}"
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import OrderItem, Restaurant

@login_required
def restaurant_dashboard(request):
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return render(request, 'restaurant/no_access.html')

    order_items = OrderItem.objects.filter(menu_item__restaurant=restaurant).select_related('order', 'menu_item')

    context = {
        'restaurant': restaurant,
        'order_items': order_items
    }
    return render(request, 'restaurant/dashboard.html', context)
