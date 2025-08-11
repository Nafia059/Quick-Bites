from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import (
    User,
    Address,
    Restaurant,
    GroceryVendor,
    Category,
    MenuItem,
    GroceryItem,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Rider,
    Delivery,
    Review,
    HelpTicket,
    PromoCode,
    Notification,
    StaticPage,
    Referral,
)

# -------------------------------
# Auth Forms
# -------------------------------

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'phone',
            'user_type',
            'profile_image',
            'referral_code',
        )
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):  # Skip file input
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'phone',
            'user_type',
            'profile_image',
            'referral_code',
        )
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

# -------------------------------
# Address Form
# -------------------------------

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            'label',
            'address_text',
            'city',
            'postal_code',
            'latitude',
            'longitude',
        )

# -------------------------------
# Restaurant Form
# -------------------------------

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = (
            'cover_photo',
            'food_type',
            'delivery_fee',
            'max_delivery_time',
        )
        widgets = {
            'max_delivery_time': forms.TimeInput(format='%H:%M:%S', attrs={'type': 'time'}),
        }

# -------------------------------
# Grocery Vendor Form
# -------------------------------

class GroceryVendorForm(forms.ModelForm):
    class Meta:
        model = GroceryVendor
        fields = (
            'store_name',
            'description',
            'address',
            'is_approved',
        )

# -------------------------------
# Category Form
# -------------------------------

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

# -------------------------------
# Menu Item Form
# -------------------------------

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = (
            'category',
            'name',
            'price',
            'image',
            'is_available',
        )

# -------------------------------
# Grocery Item Form
# -------------------------------

class GroceryItemForm(forms.ModelForm):
    class Meta:
        model = GroceryItem
        fields = (
            'category',
            'name',
            'price',
            'stock',
            'expiry_date',
            'image',
        )

# -------------------------------
# Cart Form
# -------------------------------

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ('user',)

# -------------------------------
# Cart Item Form
# -------------------------------

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = (
            'cart',
            'item_type',
            'menu_item',
            'grocery_item',
            'quantity',
        )

# -------------------------------
# Order Form
# -------------------------------

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'delivery_address',
            'payment_method',
            'status',
        )

# -------------------------------
# Order Item Form
# -------------------------------

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = (
            'menu_item',
            'grocery_item',
            'quantity',
            'price',
        )

# -------------------------------
# Payment Form
# -------------------------------

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            'status',
            'transaction_id',
        )

# -------------------------------
# Rider Form
# -------------------------------

class RiderForm(forms.ModelForm):
    class Meta:
        model = Rider
        fields = (
            'is_available',
            'current_location',
        )

# -------------------------------
# Delivery Form
# -------------------------------

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = (
            'rider',
            'status',
            'pickup_time',
            'delivery_time',
        )

# -------------------------------
# Review Form
# -------------------------------

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            'restaurant',
            'grocery_vendor',
            'rating',
            'comment',
        )

# -------------------------------
# Help Ticket Form
# -------------------------------

class HelpTicketForm(forms.ModelForm):
    class Meta:
        model = HelpTicket
        fields = (
            'subject',
            'message',
        )

# -------------------------------
# Promo Code Form
# -------------------------------

class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = (
            'code',
            'discount_percent',
            'expiry_date',
            'usage_limit',
            'is_active',
        )

# -------------------------------
# Notification Form
# -------------------------------

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = (
            'message',
            'is_read',
        )

# -------------------------------
# Static Page Form
# -------------------------------

class StaticPageForm(forms.ModelForm):
    class Meta:
        model = StaticPage
        fields = (
            'page_type',
            'content',
        )

# -------------------------------
# Referral Form
# -------------------------------

class ReferralForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = (
            'code',
            'referred_email',
            'is_used',
        )

# -------------------------------
# Checkout Form
# -------------------------------

class CheckoutForm(forms.Form):
    # Optional: select an existing address or enter a new one
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        label="Select Existing Address",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address_text = forms.CharField(
        label="New Address (if different)",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter new delivery address'}),
        required=False
    )
    city = forms.CharField(label="City", max_length=100, required=False)
    postal_code = forms.CharField(label="Postal Code", max_length=20, required=False)
    payment_method = forms.ChoiceField(
        choices=[
            ('COD', 'Cash on Delivery'),
            ('Card', 'Card Payment'),
        ],
        label="Payment Method"
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = Address.objects.filter(user=user)

# forms.py
from django import forms
from .models import Rider

class AssignRiderForm(forms.Form):
    rider = forms.ModelChoiceField(
        queryset=Rider.objects.filter(is_available=True),
        required=True,
        label="Select Rider"
    )

