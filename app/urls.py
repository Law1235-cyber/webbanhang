from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # --- CÁC TRANG CƠ BẢN ---
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # --- GIỎ HÀNG & SẢN PHẨM ---
    path('cart/', views.cart, name='cart'),
    path('add_to_cart_and_redirect/<int:pk>/', views.add_to_cart_and_redirect, name='add_to_cart_and_redirect'),
    path('update_item/', views.updateItem, name='update_item'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),

    # --- THANH TOÁN (CHECKOUT) ---
    path('checkout/', views.checkout, name='checkout'),
    path('payment-qr/<int:order_id>/', views.payment_qr, name='payment_qr'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # --- API (Backend xử lý ngầm) ---
    # 1. API cho JS gọi để kiểm tra đơn hàng đã xong chưa (Polling)
    path('api/check-payment-status/<int:order_id>/', views.check_payment_status, name='check_payment_status'),

    # 2. API Webhook nhận dữ liệu từ SePay (QUAN TRỌNG: Thêm dòng này)
    path('api/sepay-webhook/', views.sepay_webhook, name='sepay_webhook'),
    
    # Link dự phòng (nếu cần)
    path('accounts/home/', views.home, name='home_account'),
    path('products_tong/', views.product_tong, name='product_tong'),
    
]
