from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # Thêm name='home' vào đây
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    
    path('login/', views.login, name='login'),
    
    path('cart/', views.cart, name='cart'),
     
    path('checkout/', views.checkout, name='checkout'),

    path('update_item/', views.updateItem, name='update_item'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('accounts/home/', views.home, name='home'),

    path('product/<int:pk>/', views.product_detail, name='product_detail'),
     
    path('search/', views.search, name='search'),

    
    
]