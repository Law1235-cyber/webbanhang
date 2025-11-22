from django.contrib import admin
from .models import *

# Đăng ký các bảng để quản lý trong Admin
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Banner) # Đã thêm Banner