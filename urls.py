from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),

    # Menu Items
    path('menuitems/', views.menuitem_list, name='menuitem_list'),
    path('menuitems/create/', views.menuitem_create, name='menuitem_create'),
    path('menuitems/<int:pk>/update/', views.menuitem_update, name='menuitem_update'),
    path('menuitems/<int:pk>/delete/', views.menuitem_delete, name='menuitem_delete'),

    # Grocery Items
    path('groceryitems/', views.groceryitem_list, name='groceryitem_list'),
    path('groceryitems/create/', views.groceryitem_create, name='groceryitem_create'),
    path('groceryitems/<int:pk>/update/', views.groceryitem_update, name='groceryitem_update'),
    path('groceryitems/<int:pk>/delete/', views.groceryitem_delete, name='groceryitem_delete'),

    # Restaurant
    path('restaurant/update/', views.restaurant_update, name='restaurant_update'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),

    # Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/update/<int:item_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),

    # Checkout (handles order creation)
    path('checkout/', views.checkout_view, name='checkout'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/update/', views.order_update, name='order_update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),


    # Order Items
    path('orderitems/<int:order_id>/create/', views.orderitem_create, name='orderitem_create'),

    # Reviews
    path('reviews/create/', views.review_create, name='review_create'),

    # Help Tickets
    path('helptickets/', views.helpticket_list, name='helpticket_list'),
    path('helptickets/create/', views.helpticket_create, name='helpticket_create'),

    # Promo Codes
    path('promocodes/', views.promocode_list, name='promocode_list'),
    path('promocodes/create/', views.promocode_create, name='promocode_create'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),

    # Static Pages
    path('staticpages/<int:pk>/update/', views.staticpage_update, name='staticpage_update'),

    # Referrals
    path('referrals/', views.referral_list, name='referral_list'),

    # Rider
    path('rider/update/', views.rider_update, name='rider_update'),

    # Delivery
    path('deliveries/<int:pk>/update/', views.delivery_update, name='delivery_update'),

    # Auth (Login, Signup, Logout)
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('payment/card/<int:order_id>/', views.card_payment_view, name='card_payment'),

   
path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),

# urls.py
path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
path('rider/dashboard/', views.rider_dashboard, name='rider_dashboard'),
path('rider/delivery/<int:delivery_id>/update/', views.update_delivery_status, name='update_delivery_status'),

path('my-orders/', views.customer_orders, name='customer_orders'),
path('save_location/', views.save_location, name='save_location'),

]

