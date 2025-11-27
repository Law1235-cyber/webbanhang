from .models import Cart

def cart_context(request):
    """
    Thêm số lượng mặt hàng trong giỏ hàng vào context của tất cả các template.
    - cartItems: Số lượng mặt hàng trong giỏ hàng (sử dụng model Cart).
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
            
    return {'cartItems': cartItems}
