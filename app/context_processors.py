# app/context_processors.py

from .models import Customer, Order, Product # Đảm bảo bạn import đúng models
from django.contrib.auth.models import User

def cart_context(request):
    """
    Thêm các biến dùng chung vào context của TẤT CẢ các template.
    - cartItems: Số lượng mặt hàng trong giỏ hàng.
    - products: Tất cả sản phẩm để hiển thị.
    """
    cartItems = 0
    if request.user.is_authenticated:
        try:
            # Lấy hoặc tạo Customer cho người dùng đã đăng nhập
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={'name': request.user.username, 'email': request.user.email}
            )
            
            # Lấy Order chưa hoàn thành (Giỏ hàng)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
            
        except Exception:
            # Xử lý nếu có lỗi xảy ra (ví dụ: Customer model bị lỗi)
            cartItems = 0

    # Lấy tất cả sản phẩm
    products = Product.objects.all()

    return {'cartItems': cartItems, 'products': products}