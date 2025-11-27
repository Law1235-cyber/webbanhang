import os
from django.db import models
from django.contrib.auth.models import User

# ==============================================================================
# PHẦN 1: CATALOGUE (DANH MỤC & SẢN PHẨM CỐT LÕI)
# ==============================================================================

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name or f"Category #{self.id}"

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Giá bán")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng tồn kho")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Thông số kỹ thuật (Dữ liệu Laptop)
    cpu = models.CharField(max_length=200, null=True, blank=True, verbose_name="Vi xử lý (CPU)")
    ram = models.CharField(max_length=200, null=True, blank=True, verbose_name="RAM")
    storage = models.CharField(max_length=200, null=True, blank=True, verbose_name="Ổ cứng")
    screen = models.CharField(max_length=200, null=True, blank=True, verbose_name="Màn hình")
    vga = models.CharField(max_length=200, null=True, blank=True, verbose_name="Card màn hình")
    os = models.CharField(max_length=200, null=True, blank=True, verbose_name="Hệ điều hành")
    battery = models.CharField(max_length=200, null=True, blank=True, verbose_name="Pin")
    weight = models.CharField(max_length=200, null=True, blank=True, verbose_name="Trọng lượng")

    def __str__(self):
        return self.name or f"Product #{self.id}"

    @property
    def imageURL(self):
        return self.image.url if self.image else ''

# ==============================================================================
# PHẦN 2: HỆ THỐNG GIỎ HÀNG (CART SYSTEM) - DỮ LIỆU ĐỘNG
# ==============================================================================

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} (User: {self.user.username if self.user else 'Guest'})"

    @property
    def get_cart_total(self):
        cart_items = self.cartitem_set.all()
        return sum([item.get_total for item in cart_items])

    @property
    def get_cart_items(self):
        return sum([item.quantity for item in self.cartitem_set.all()])

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    @property
    def get_total(self):
        return self.product.price * self.quantity

# ==============================================================================
# PHẦN 3: HỆ THỐNG ĐƠN HÀNG (ORDER SYSTEM) - DỮ LIỆU BẤT BIẾN (SNAPSHOT)
# ==============================================================================

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Chờ xử lý'),
        ('Paid', 'Đã thanh toán'),
        ('Shipping', 'Đang giao hàng'),
        ('Completed', 'Hoàn thành'),
    )

    # Thông tin cơ bản & Khóa ngoại
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    complete = models.BooleanField(default=False)
    
    # THÔNG TIN GIAO HÀNG SNAPSHOT (LƯU TRỮ LỊCH SỬ)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tổng tiền chốt đơn")
    shipping_name = models.CharField(max_length=200)
    shipping_mobile = models.CharField(max_length=20)
    shipping_address = models.CharField(max_length=500)
    shipping_city = models.CharField(max_length=100)
    shipping_quocgia = models.CharField(max_length=100, default="Việt Nam") # Tên cột bạn dùng là quocgia

    # Thanh toán
    payment_method = models.CharField(max_length=50, null=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} ({self.shipping_name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_original = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # TRƯỜNG SNAPSHOT (GIÁ TRỊ CỐ ĐỊNH TẠI THỜI ĐIỂM MUA)
    product_name_snapshot = models.CharField(max_length=200)
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2) 
    quantity = models.IntegerField(default=1)
    
    @property
    def get_total(self):
        return self.price_at_purchase * self.quantity


# ==============================================================================
# PHẦN 4: CÁC MODEL KHÁC (CUSTOMER PROFILE, COMMENT, BANNER, LOGO)
# ==============================================================================

# Giữ lại Customer cũ để lưu profile cá nhân (tách biệt khỏi Order)
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    # ... (Các trường profile khác) ...

    def __str__(self):
        return self.user.username if self.user else 'Guest'
    
    @property
    def total_order_items(self):
        # Thuộc tính này giờ cần được xóa hoặc cập nhật để lấy từ Cart mới (nếu muốn dùng lại)
        # Tạm thời để nó an toàn
        return 0 


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Banner(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='banners/')
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name or 'Banner'

class logo(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to='logo/')
    def __str__(self):
        return str(self.image) or 'Logo'