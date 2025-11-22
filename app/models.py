import os
from django.db import models
from django.contrib.auth.models import User

# createUserForm has been moved to app/forms.py

# ------------------ MODEL 1: CUSTOMER ------------------

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name or 'N/A' # Trả về 'N/A' nếu name là None

    @property
    def total_order_items(self):
        """Tính tổng số lượng sản phẩm trong giỏ hàng (đơn hàng chưa hoàn thành)."""
        order = self.order_set.filter(complete=False).first()
        if order:
            items = order.orderitem_set.all()
            return sum(item.quantity for item in items)
        return 0


# ------------------ MODEL 2: PRODUCT ------------------
class Product(models.Model):
    name = models.CharField(max_length=100, null=True, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete the image file before deleting the Product object
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    @property
    def imageURL(self):
        """Trả về URL hình ảnh, xử lý trường hợp không có hình ảnh."""
        try:
            url = self.image.url
        except:
            url = ''
        return url


# ------------------ MODEL 3: ORDER ------------------
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        """Tính tổng giá trị của tất cả OrderItem trong đơn hàng này."""
        orderitems = self.orderitem_set.all()
        total = sum(item.get_total for item in orderitems)
        return total

    @property
    def get_cart_items(self):
        """Tính tổng số lượng sản phẩm trong đơn hàng này."""
        orderitems = self.orderitem_set.all()
        total = sum(item.quantity for item in orderitems)
        return total


# ------------------ MODEL 4: ORDER ITEM ------------------
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True, null=True, blank=True)

    @property
    def get_total(self):
        """Tính tổng giá trị của một mục hàng (sản phẩm * số lượng)."""
        if self.product and self.product.price is not None:
            total = self.product.price * self.quantity
            return total
        return 0


# ------------------ MODEL 5: SHIPPING ADDRESS ------------------
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=10, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True, null=True, blank=True)
    quocgia = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.address or 'N/A'


class Banner(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='banners/')
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name or 'N/A'