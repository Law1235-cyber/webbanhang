from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json # Đảm bảo đã có import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
import json
from .models import Product, Comment
from .forms import CommentForm

# Import các Models và Forms
from .models import Customer, Order, OrderItem, Product, Banner, Category, Cart, CartItem 
from .forms import CommentForm, createUserForm

# --- 1. TRANG CHỦ ---
def home(request):
    products = Product.objects.all()
    banners = Banner.objects.all()
    categories = Category.objects.all()
    context = {'products': products, 'banners': banners, 'categories': categories}
    return render(request, 'app/home.html', context)

# --- 2. TÌM KIẾM ---
def search(request):
    query = request.GET.get('q')
    products = []
    
    if query:
        # Tìm kiếm không phân biệt hoa thường
        products = Product.objects.filter(
            Q(name__icontains=query)
        ).distinct()

    context = {'products': products, 'query': query}
    return render(request, 'app/search_results.html', context)

# --- 3. CHI TIẾT SẢN PHẨM ---
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Xử lý khi người dùng gửi bình luận
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.product = product
                comment.user = request.user
                comment.save()
                return redirect('product_detail', pk=pk) # Load lại trang để hiện bình luận mới
        else:
            return redirect('login')

    else:
        form = CommentForm()

    # Lấy danh sách bình luận (Mới nhất lên đầu)
    comments = Comment.objects.filter(product=product).order_by('-date_added')

    context = {
        'product': product,
        'comments': comments,
        'form': form
    }
    return render(request, 'app/product_detail.html', context)

# --- 4. ĐĂNG KÝ ---
def register(request):
    form = createUserForm()
    if request.method == 'POST':
        form = createUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user=user,
                name=user.username,
                email=user.email,
            )
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
            return redirect('home')
    else:
        form = AuthenticationForm()
        
    context = {'form': form}
    return render(request, 'app/login.html', context)

# --- 6. GIỎ HÀNG (CART) - ĐÃ SỬA LỖI LOGIC CART/ORDER ---
def cart(request):
    if request.user.is_authenticated:
        # 1. Lấy hoặc tạo Customer Profile
        customer, created = Customer.objects.get_or_create(
            user=request.user,
            defaults={'name': request.user.username, 'email': request.user.email}
        )
        # 2. Lấy hoặc tạo Cart liên kết trực tiếp với User
        # Đã tối ưu Query bằng prefetch_related để giảm N+1
        cart = Cart.objects.prefetch_related('cartitem_set__product').get_or_create(user=request.user)[0] 
        items = cart.cartitem_set.all() # Lấy CartItem (sản phẩm trong giỏ)
        
        # Truyền thông tin tổng hợp của Cart cho template (Sử dụng property từ model Cart)
        order_info = {'get_cart_total': cart.get_cart_total, 'get_cart_items': cart.get_cart_items}
        cartItems = cart.get_cart_items
        
    else:
        # Xử lý cho khách vãng lai (Guest) - Cần dùng Session nếu muốn lưu Giỏ hàng
        # Hiện tại, chỉ hiển thị trống
        items = []
        order_info = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
        
    context = {'items': items, 'order': order_info, 'cartItems': cartItems} 
    return render(request, 'app/cart.html', context)

# --- 7. THANH TOÁN (CHECKOUT) - ĐÃ SỬA LỖI VÀ THÊM LOGIC TẠO SNAPSHOT ---
def checkout(request):
    # Buộc đăng nhập để thanh toán
    if not request.user.is_authenticated:
        return redirect('login') 
        
    customer = Customer.objects.get(user=request.user)
    cart = Cart.objects.get_or_create(user=request.user)[0]
    cart_items = cart.cartitem_set.all()
    
    # Bắt buộc Giỏ hàng phải có sản phẩm
    if not cart_items.exists():
        return redirect('cart')

    # Lấy thông tin Giỏ hàng để hiển thị
    order_info = {'get_cart_total': cart.get_cart_total, 'get_cart_items': cart.get_cart_items, 'id': 0}
    cartItems = cart.get_cart_items
    
    # 2. Xử lý khi người dùng bấm nút "Tiếp tục" (POST request)
    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        mobile = request.POST.get('mobile')
        payment_method = request.POST.get('paymentMethod') or 'COD' # Mặc định là COD
        
        # --- A. TẠO ORDER MỚI (SNAPSHOT) ---
        new_order = Order.objects.create(
            customer=request.user, # Khóa ngoại đến User
            total_amount=cart.get_cart_total, # Tổng tiền chốt đơn
            shipping_name=name,
            shipping_mobile=mobile,
            shipping_address=address,
            shipping_city=city,
            shipping_quocgia='Vietnam', # Giả định (Cần thay bằng trường thích hợp)
            payment_method=payment_method
        )

        # --- B. TẠO ORDER ITEM (SNAPSHOT CỦA TỪNG SẢN PHẨM) ---
        for item in cart_items:
            OrderItem.objects.create(
                order=new_order,
                product_original=item.product, 
                product_name_snapshot=item.product.name,
                price_at_purchase=item.product.price, # Giá cố định tại thời điểm mua
                quantity=item.quantity
            )
            # Cập nhật số lượng tồn kho (Nếu cần thiết, nên dùng transaction)
            # item.product.quantity -= item.quantity
            # item.product.save()

        # --- C. XÓA CART CŨ SAU KHI TẠO ĐƠN THÀNH CÔNG ---
        cart.cartitem_set.all().delete()
        
        # --- D. ĐIỀU HƯỚNG THEO PHƯƠNG THỨC THANH TOÁN ---
        if payment_method == 'Online':
            # Chuyển sang trang QR Code
            return redirect('payment_qr', order_id=new_order.id)
        else:
            # COD: Đơn hàng đã được tạo. Chuyển trạng thái ban đầu
            new_order.status = 'Pending' 
            new_order.save()
            return redirect('payment_success')

    context = {
        'items': cart_items, 
        'order': order_info, 
        'cartItems': cartItems, 
        'customer': customer,
    }
    return render(request, 'app/checkout.html', context)

# --- 8. CẬP NHẬT GIỎ HÀNG (AJAX) - ĐÃ SỬA LỖI LOGIC CART/ORDER ---
def updateItem(request):
    if request.method != 'POST':
        return JsonResponse('Only POST requests allowed', status=405, safe=False)
        
    if not request.user.is_authenticated:
        return JsonResponse('User is not authenticated', safe=False)

    try:
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')
        
        product = Product.objects.get(id=productId)
        
        # 1. Lấy Giỏ hàng của User hiện tại (Đảm bảo tính cá nhân hóa)
        cart, created = Cart.objects.get_or_create(user=request.user) 
        
        # 2. Lấy hoặc tạo CartItem trong Cart đó
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product) 
        
        # Logic cập nhật số lượng
        if action == 'add':
            # Nếu item chưa có trong giỏ, 'created' sẽ là True, và số lượng mặc định là 1.
            # Nếu đã có, 'created' là False, chúng ta sẽ cộng thêm 1.
            if not created:
                cart_item.quantity += 1
        elif action == 'remove':
            cart_item.quantity -= 1
        elif action == 'delete':
            cart_item.quantity = 0 # Đặt về 0 để xóa
            
        cart_item.save()

        if cart_item.quantity <= 0:
            cart_item.delete() # Xóa CartItem khỏi Database
            
        # Trả về tổng số lượng sản phẩm mới trong giỏ hàng
        total_items = cart.get_cart_items
        return JsonResponse({'message': 'Item was updated', 'total_items': total_items})
        
    except Product.DoesNotExist:
        return JsonResponse('Product not found', status=404, safe=False)
    except Exception as e:
        return JsonResponse(f'Error: {e}', status=400, safe=False)

# --- 9. TRANG HIỂN THỊ MÃ QR ---
def payment_qr(request, order_id):
    # Sử dụng get_object_or_404 để an toàn hơn
    order = get_object_or_404(Order, id=order_id)
    
    # Nếu đơn hàng đã hoàn tất, không cho thanh toán lại
    if order.status == 'Completed':
        return redirect('payment_success')
        
    context = {'order': order}
    return render(request, 'app/payment_qr.html', context)

# --- 10. API KIỂM TRA TRẠNG THÁI (Cho Javascript ở trang QR) ---
def check_payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return JsonResponse({'complete': order.status == 'Completed'})
    except Order.DoesNotExist:
        return JsonResponse({'complete': False})

# --- 11. TRANG THÔNG BÁO THÀNH CÔNG ---
def payment_success(request):
    # Render file HTML thông báo đẹp mắt
    return render(request, 'app/payment_success.html')

# --- 12. WEBHOOK XỬ LÝ THANH TOÁN TỰ ĐỘNG (SePay) ---
@csrf_exempt
def sepay_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Lấy các thông tin từ SePay
            transferContent = data.get('content')
            transferAmount = data.get('transferAmount')
            transferType = data.get('transferType')
            transaction_id = data.get('referenceCode')

            # Chỉ xử lý giao dịch tiền vào (in)
            if transferType != 'in':
                return JsonResponse({'success': False, 'message': 'Not an incoming transaction'})

            # --- LOGIC TÌM ORDER ID ---
            # Lọc lấy số từ nội dung chuyển khoản (VD: "DH123" -> 123)
            order_id_str = ''.join(filter(str.isdigit, transferContent))
            
            if not order_id_str:
                 return JsonResponse({'success': False, 'message': 'No Order ID found in content'})

            order_id = int(order_id_str)

            # Tìm đơn hàng trong Database
            order = Order.objects.filter(id=order_id).first()

            if order:
                # Kiểm tra số tiền (phải lớn hơn hoặc bằng tổng tiền đơn hàng)
                cart_total = float(order.total_amount)
                
                if transferAmount >= cart_total:
                    order.status = 'Paid'
                    order.transaction_id = transaction_id
                    order.payment_method = 'Online' # Cập nhật phương thức thanh toán
                    order.save()
                    
                    print(f"WEBHOOK: Đơn hàng {order_id} đã thanh toán thành công!")
                    return JsonResponse({'success': True, 'message': 'Payment confirmed'})
                else:
                    return JsonResponse({'success': False, 'message': 'Amount mismatch'})
            else:
                 return JsonResponse({'success': False, 'message': 'Order not found'})

        except Exception as e:
            print("Lỗi Webhook:", e)
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid method'})


# app/views.py

# --- 13. TRANG HIỂN THỊ TẤT CẢ SẢN PHẨM (Có Lọc Danh Mục + Giá + Phân trang) ---
def product_tong(request):
    products = Product.objects.all()
    categories = Category.objects.all() # 1. Lấy tất cả danh mục để hiển thị

    # --- LOGIC LỌC DANH MỤC (Mới thêm) ---
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category__id=category_id)

    # --- LOGIC LỌC GIÁ (Giữ nguyên) ---
    price_filter = request.GET.get('price')
    if price_filter == 'under10':
        products = products.filter(price__lt=10000000)
    elif price_filter == '10to20':
        products = products.filter(price__gte=10000000, price__lte=20000000)
    elif price_filter == 'above20':
        products = products.filter(price__gt=20000000)

    # --- LOGIC SẮP XẾP (Giữ nguyên) ---
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-id')

    # --- LOGIC PHÂN TRANG (Giữ nguyên) ---
    paginator = Paginator(products, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Truyền thêm 'categories' vào context
    context = {'page_obj': page_obj, 'categories': categories} 
    return render(request, 'app/product.html', context)


# --- 14. TRANG HỒ SƠ KHÁCH HÀNG (PROFILE) ---
@login_required
def profile(request):
    # Lấy thông tin Customer liên quan đến User đang đăng nhập
    customer = get_object_or_404(Customer, user=request.user)
    
    # Lấy tất cả đơn hàng của user, sắp xếp theo ngày tạo mới nhất
    # Sử dụng prefetch_related để tối ưu, lấy tất cả OrderItem cùng lúc
    orders = Order.objects.filter(customer=request.user).prefetch_related('items', 'items__product_original').order_by('-date_ordered')
    
    # Phân loại đơn hàng
    current_orders = [order for order in orders if order.status in ['Pending', 'Shipping']]
    past_orders = [order for order in orders if order.status in ['Paid', 'Completed']]
    
    context = {
        'customer': customer,
        'current_orders': current_orders,
        'past_orders': past_orders,
    }
    return render(request, 'app/profile.html', context)

