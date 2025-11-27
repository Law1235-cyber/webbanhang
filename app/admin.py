from django.contrib import admin
from .models import * # (Model ProductDetail đã được thay bằng các trường trong Product để đơn giản)


# ------------------- 1. INLINES (Các mục con) -------------------

# Mục con cho Cart (Hiển thị các sản phẩm trong Giỏ hàng)
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0 # Không hiển thị thêm dòng trống mặc định
    fields = ('product', 'quantity', 'get_total',)
    readonly_fields = ('get_total',)


# Mục con cho Order (Hiển thị các sản phẩm trong Đơn hàng)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Đơn hàng là lịch sử, không cho phép sửa giá/tên
    readonly_fields = ('product_original', 'product_name_snapshot', 'price_at_purchase', 'quantity', 'get_total',)
    extra = 0
    can_delete = False # Không cho phép xóa mục hàng khỏi đơn hàng lịch sử

    def has_add_permission(self, request, obj):
        return False # Không cho phép thêm thủ công sau khi chốt đơn

# ------------------- 2. ADMIN CHO CÁC MODEL CHÍNH -------------------

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'category', 'imageURL')
    list_filter = ('category',)
    search_fields = ('name', 'cpu', 'ram', 'storage') # Có thể tìm theo thông số kỹ thuật
    list_per_page = 20


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('id', 'user', 'get_cart_items', 'get_cart_total', 'created_at')
    readonly_fields = ('get_cart_total', 'get_cart_items', 'user', 'created_at')
    search_fields = ('user__username',)


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'shipping_name', 'total_amount', 'status', 'date_ordered', 'payment_method')
    list_filter = ('status', 'payment_method', 'date_ordered')
    search_fields = ('shipping_name', 'shipping_address', 'transaction_id')
    # Order là lịch sử, chỉ có status là được sửa, còn lại là readonly
    readonly_fields = ('date_ordered', 'total_amount', 'shipping_name', 'shipping_address', 'payment_method', 'transaction_id')


# ------------------- 3. ĐĂNG KÝ VÀ ÁP DỤNG -------------------

# Đăng ký các Model phụ (Không cần tùy chỉnh nhiều)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Banner)
admin.site.register(logo)

# Đăng ký các Model chính với Custom Admin
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)

# Loại bỏ đăng ký model ShippingAddress (đã bị xóa/gộp vào Order)
# admin.site.register(ShippingAddress) # Đảm bảo dòng này đã được xóa