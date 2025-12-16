from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json # Đảm bảo đã có import json
import logging # Add logging for debugging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
import json
import re
from .models import Product, Comment
from .forms import CommentForm

# Import các Models và Forms
from .models import Customer, Order, OrderItem, Product, Banner, Category, Cart, CartItem, logo 
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
    
    # Kiểm tra xem người dùng đã mua sản phẩm này chưa
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            customer=request.user, 
            status__in=['Paid', 'Completed'], 
            items__product_original=product
        ).exists()

    # Xử lý khi người dùng gửi bình luận
    if request.method == 'POST':
        if has_purchased: # Chỉ cho phép bình luận nếu đã mua
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.product = product
                comment.user = request.user
                comment.save()
                return redirect('product_detail', pk=pk)
        else:
            # Nếu chưa mua mà cố tình POST, bỏ qua và load lại trang
            return redirect('product_detail', pk=pk)

    else:
        form = CommentForm()

    # Lấy danh sách bình luận (Mới nhất lên đầu)
    comments = Comment.objects.filter(product=product).order_by('-date_added')

    context = {
        'product': product,
        'comments': comments,
        'form': form,
        'has_purchased': has_purchased # Truyền biến này cho template
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

# --- VIEW TRANG CÁ NHÂN (PROFILE) ---
@login_required(login_url='login')
def profile(request):
    customer = get_object_or_404(Customer, user=request.user)
    
    # Lấy các đơn hàng đã hoàn thành (Lịch sử)
    past_orders = Order.objects.filter(customer=request.user, complete=True).order_by('-date_ordered')
    
    # Lấy các đơn hàng chưa hoàn thành (Hiện tại)
    current_orders = Order.objects.filter(customer=request.user, complete=False).order_by('-date_ordered')

    context = {
        'customer': customer, 
        'past_orders': past_orders,
        'current_orders': current_orders
    }
    return render(request, 'app/profile.html', context)


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
    
    shipping_address = None
    try:
        # Lấy địa chỉ giao hàng gần nhất từ model ShippingAddress
        shipping_address = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()
    except NameError:
        # Xử lý nếu model ShippingAddress chưa được định nghĩa
        pass
        
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
            complete=False, # Explicitly set complete to False on creation
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
        cart.delete()
        
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
        'shipping_address': shipping_address
    }
    return render(request, 'app/checkout.html', context)

# --- 8. CẬP NHẬT GIỎ HÀNG (AJAX) - ĐÃ SỬA LỖI LOGIC CART/ORDER ---
def updateItem(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
        
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

    try:
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')

        if not productId or not action:
            return JsonResponse({'error': 'productId and action are required'}, status=400)

        product = Product.objects.get(id=productId)
        cart, cart_created = Cart.objects.get_or_create(user=request.user)
        
        # --- FIX for MultipleObjectsReturned ---
        # This logic now handles cases where duplicate CartItems might exist.
        
        # 1. Get all items for this product in the cart.
        cart_items = CartItem.objects.filter(cart=cart, product=product)
        
        cart_item = None
        if cart_items.exists():
            # 2. Consolidate duplicates into the first item.
            cart_item = cart_items.first()
            
            # If there are more than one, sum quantities and delete extras.
            if cart_items.count() > 1:
                total_quantity = sum(item.quantity for item in cart_items)
                cart_item.quantity = total_quantity
                # Delete the other duplicate items.
                cart_items.exclude(pk=cart_item.pk).delete()
        else:
            # 3. If no item exists, create a new one with quantity 0.
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=0)

        # 4. Now, apply the action to the single, consolidated item.
        if action == 'add':
            cart_item.quantity += 1
        elif action == 'remove':
            cart_item.quantity -= 1
        elif action == 'delete':
            cart_item.quantity = 0
            
        cart_item.save()

        # 5. If quantity is zero or less, delete the item.
        if cart_item.quantity <= 0:
            cart_item.delete()
            
        # 6. Return the total number of items in the cart.
        total_items = cart.get_cart_items
        return JsonResponse({'message': 'Item was updated successfully', 'total_items': total_items})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        # Log the exception for admin/developer review
        print(f"Error in updateItem: {e}") 
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

# --- 9. TRANG HIỂN THỊ MÃ QR ---
def payment_qr(request, order_id):
    # Sử dụng get_object_or_404 để an toàn hơn
    order = get_object_or_404(Order, id=order_id)
    
    # Nếu đơn hàng đã hoàn tất, không cho thanh toán lại
    if order.complete:
        return redirect('payment_success')
        
    context = {'order': order}
    return render(request, 'app/payment_qr.html', context)

# --- 10. API KIỂM TRA TRẠNG THÁI (Cho Javascript ở trang QR) ---
def check_payment_status(request, order_id):
    try:
        # Sử dụng .values() để chỉ lấy trường 'complete' và tránh các vấn đề về ORM object caching.
        # .first() sẽ trả về một dict (vd: {'complete': True}) hoặc None nếu không tìm thấy.
        order_status = Order.objects.filter(id=order_id).values('complete').first()

        if order_status:
            # Nếu tìm thấy, trả về giá trị của 'complete'.
            return JsonResponse({'complete': order_status['complete']})
        else:
            # Nếu không tìm thấy đơn hàng, trả về False.
            return JsonResponse({'complete': False, 'error': 'Order not found'})
            
    except Exception as e:
        logging.error(f"Lỗi trong check_payment_status cho order {order_id}: {e}")
        return JsonResponse({'complete': False, 'error': 'An error occurred'})

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
            transferAmount = data.get('transferAmount')
            transferContent = data.get('content')
            transferType = data.get('transferType')
            transaction_id = data.get('referenceCode')

            # Kiểm tra giao dịch tiền vào (in)
            if transferType != 'in':
                return JsonResponse({'success': False, 'message': 'Not an incoming transaction'})

            # --- CÔNG NGHỆ MỚI: Dùng Regex tìm chữ "DH" + Số ---
            # Chỉ bắt những nội dung có dạng "DH15", "dh15", "DH 15"
            match = re.search(r'DH(\d+)', transferContent, re.IGNORECASE)
            
            if not match:
                 return JsonResponse({'success': False, 'message': 'No Order ID pattern (e.g., DH15) found in content'})

            order_id = int(match.group(1)) # Lấy con số 15 ra

            # Tìm đơn hàng
            order = Order.objects.filter(id=order_id).first()

            if order:
                # --- SỬA LỖI QUAN TRỌNG TẠI ĐÂY ---
                # Dùng total_amount (Trường lưu giá cố định trong Order)
                order_total = float(order.total_amount)
                
                # So sánh số tiền (dùng >= để an toàn phòng khi khách chuyển dư)
                if transferAmount >= order_total:
                    order.complete = True
                    order.status = 'Paid' # Cập nhật thêm trạng thái text cho rõ ràng
                    order.transaction_id = transaction_id
                    order.payment_method = 'Online'
                    order.save()
                    
                    print(f"WEBHOOK: Đơn hàng {order_id} đã thanh toán thành công!")
                    return JsonResponse({'success': True, 'message': 'Payment confirmed'})
                else:
                    # In log chi tiết để dễ debug nếu khách chuyển thiếu
                    print(f"WEBHOOK: Sai số tiền đơn {order_id}. Nhận: {transferAmount}, Cần: {order_total}")
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

@login_required(login_url='login')
def add_to_cart_and_redirect(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        product = Product.objects.get(id=pk)
        cart, cart_created = Cart.objects.get_or_create(user=request.user)
        
        cart_items = CartItem.objects.filter(cart=cart, product=product)
        
        cart_item = None
        if cart_items.exists():
            cart_item = cart_items.first()
            if cart_items.count() > 1:
                total_quantity = sum(item.quantity for item in cart_items)
                cart_item.quantity = total_quantity
                cart_items.exclude(pk=cart_item.pk).delete()
        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=0)

        cart_item.quantity += 1
        cart_item.save()

    except Product.DoesNotExist:
        pass 
    except Exception as e:
        print(f"Error in add_to_cart_and_redirect: {e}")

    return redirect('cart')
