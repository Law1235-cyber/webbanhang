# app/views.py - Code đã được dọn dẹp và tối ưu hóa cho người mới học

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse 
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
import json

# Giả định form đăng ký đã được import từ app/forms.py
from .models import Customer, Order, OrderItem, Product, ShippingAddress, Banner
from .forms import createUserForm


# --- 1. TRANG CHỦ ---
def home(request):
    products = Product.objects.all()
    banners = Banner.objects.all()
    context = {'products': products, 'banners': banners}
    return render(request, 'app/home.html', context)
   

# --- 2. TÌM KIẾM ---
def search(request):
    query = request.GET.get('q') 
    products = []
    
    if query:
        # Tìm kiếm không phân biệt chữ hoa/thường trong tên sản phẩm
        products = Product.objects.filter(
            Q(name__icontains=query)
        ).distinct()

    context = {'products': products, 'query': query}
    return render(request, 'app/search_results.html', context)

# --- 3. CHI TIẾT SẢN PHẨM ---
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'app/product_detail.html', context)

# --- 4. ĐĂNG KÝ ---
def register(request):
    # Dùng form tùy chỉnh (createUserForm) đã thêm email
    form = createUserForm()
    
    if request.method == 'POST':
        form = createUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tự động tạo hồ sơ Customer khi đăng ký thành công
            Customer.objects.create(
                user=user,
                name=user.username,
                email=user.email,
            )
            # Chuyển hướng đến trang đăng nhập sau khi đăng ký
            return redirect('login') 
            
    context={'form': form}
    return render(request, 'app/register.html', context)

# --- 5. ĐĂNG NHẬP ---
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # Chuyển hướng về trang chủ sau khi đăng nhập thành công
            return redirect('home') 
    else:
        form = AuthenticationForm()
        
    context = {'form': form}
    return render(request, 'app/login.html', context)

# --- 6. GIỎ HÀNG (CART) ---
def cart(request):
    if request.user.is_authenticated:
        # Lấy hoặc tạo Customer cho người dùng hiện tại
        customer, created = Customer.objects.get_or_create(
            user=request.user,
            defaults={'name': request.user.username, 'email': request.user.email}
        )
        
        # Lấy hoặc tạo Đơn hàng CHƯA hoàn thành (giỏ hàng)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Xử lý cho người dùng khách (Guest)
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
        
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'app/cart.html', context)

# --- 7. THANH TOÁN (CHECKOUT) ---
def checkout(request):
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = 0
    customer = None
    shipping_address = None

    if request.user.is_authenticated:
        customer, created_cust = Customer.objects.get_or_create(
            user=request.user,
            defaults={'name': request.user.username, 'email': request.user.email}
        )
        
        order, created_order = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        try:
            # Lấy địa chỉ giao hàng cuối cùng đã lưu
            shipping_address = ShippingAddress.objects.filter(customer=customer).order_by('date_added').first()
        except ShippingAddress.DoesNotExist:
            pass # Giữ shipping_address là None
            
    # Context chứa tất cả dữ liệu cần thiết cho trang checkout
    context = { 
        'items': items, 
        'order': order, 
        'cartItems': cartItems,
        'customer': customer,
        'shipping_address': shipping_address
    }
    return render(request, 'app/checkout.html', context)

# --- 8. CẬP NHẬT GIỎ HÀNG (AJAX) ---
def updateItem(request):
    if request.method != 'POST':
        return JsonResponse('Only POST requests allowed', status=405, safe=False)
        
    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    try:
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')
        
        if not productId or not action:
            return JsonResponse('Missing data', status=400, safe=False)

        # Đảm bảo Customer tồn tại và xử lý logic giỏ hàng
        customer, created_cust = Customer.objects.get_or_create(
            user=request.user,
            defaults={'name': request.user.username or 'Guest', 'email': request.user.email or ''}
        )
        
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            order_item.quantity += 1
        elif action == 'remove':
            order_item.quantity -= 1
        elif action == 'delete':
            order_item.quantity = 0
            
        order_item.save()

        # Xóa OrderItem nếu số lượng bằng 0 hoặc ít hơn
        if order_item.quantity <= 0:
            order_item.delete()
            
        return JsonResponse('Item was updated', safe=False)
        
    except Product.DoesNotExist:
        return JsonResponse('Product not found', status=404, safe=False)
    except Exception as e:
        print(f"Error in updateItem: {e}")
        return JsonResponse(f'Error: {e}', status=400, safe=False)