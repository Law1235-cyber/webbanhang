from .models import Cart, logo

def cart_context(request):
    """
    Thêm số lượng mặt hàng trong giỏ hàng và logo vào context của tất cả các template.
    - cartItems: Số lượng mặt hàng trong giỏ hàng (sử dụng model Cart).
    - logo: Đối tượng logo để hiển thị trên trang.
    """
    cartItems = 0
    if request.user.is_authenticated:
        try:
            # Lấy giỏ hàng (Cart) được liên kết với người dùng
            cart = Cart.objects.get(user=request.user)
            cartItems = cart.get_cart_items
        except Cart.DoesNotExist:
            # Nếu người dùng đã đăng nhập nhưng chưa có giỏ hàng, cartItems vẫn là 0
            cartItems = 0
    
    # Lấy tất cả các đối tượng logo
    logos = logo.objects.all()
    
    return {
        'cartItems': cartItems,
        'logo': logos
    }
