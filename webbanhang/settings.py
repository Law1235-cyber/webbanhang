"""
Django settings for webbanhang project.
Updated for Render Deployment (Supabase + Cloudinary + WhiteNoise)
"""

import os
from pathlib import Path
import dj_database_url  # Thư viện để kết nối Database Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CẤU HÌNH BẢO MẬT ---

# Lấy Secret Key từ biến môi trường Render, nếu không có thì dùng key mặc định (để chạy local không lỗi)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-key-du-phong-khi-chay-o-nha')

# Tự động tắt DEBUG khi lên Render để bảo mật (Render set DEBUG=False)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Cho phép mọi tên miền truy cập (Quan trọng để Render chạy được)
ALLOWED_HOSTS = ['*']


# --- CẤU HÌNH APP ---

INSTALLED_APPS = [
    'jazzmin',                  # Giao diện Admin đẹp (Phải để đầu)
    'cloudinary_storage',       # Lưu trữ ảnh trên Cloudinary
    'cloudinary',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app',                      # App của bạn
    'widget_tweaks',            # Chỉnh sửa form
    'django_cleanup.apps.CleanupConfig', # Tự động xóa ảnh thừa
    
    # Các thư viện khác nếu bạn có dùng (rest_framework, allauth...) thêm vào dưới đây
    'rest_framework',
    'rest_framework_simplejwt',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <--- QUAN TRỌNG: Để load CSS/JS trên Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Middleware cho allauth (nếu dùng)
]

ROOT_URLCONF = 'webbanhang.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.cart_context', # Context giỏ hàng của bạn
            ],
        },
    },
]

WSGI_APPLICATION = 'webbanhang.wsgi.application'


# --- CẤU HÌNH DATABASE (QUAN TRỌNG) ---

# Tự động chọn Database:
# - Nếu trên Render (có biến DATABASE_URL): Dùng Supabase (PostgreSQL)
# - Nếu ở máy nhà (không có biến đó): Dùng SQLite
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}


# --- CẤU HÌNH PASSWORD ---

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# --- CẤU HÌNH QUỐC TẾ HÓA ---

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- CẤU HÌNH STATIC FILES (CSS/JS - WHITE NOISE) ---
# Đây là phần sửa lỗi "AttributeError: STATICFILES_STORAGE"

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Nơi Render gom file tĩnh vào

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Nơi chứa file static gốc của bạn
]

# Sử dụng WhiteNoise để nén và phục vụ file tĩnh
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- CẤU HÌNH MEDIA (CLOUDINARY) ---

# Thông tin Cloudinary của bạn
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dhtqwmp9f', 
    'API_KEY': '445756636998613',    
    'API_SECRET': 'L-4Ds71mVU6SL9y3z1-_Od1_Zto'  
}

# Báo Django lưu ảnh lên Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'


# --- CẤU HÌNH KHÁC ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/' # Đăng nhập xong về trang chủ