"""
Django settings for webbanhang project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Ưu tiên lấy từ biến môi trường trên Render, nếu không có thì dùng key mặc định (để chạy local)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#&t(x&a6$w9o*q#n2so6(niikk5__7dmdpfj7g6&5k%_7*3af&')

# SECURITY WARNING: don't run with debug turned on in production!
# Tự động False trên Render, True trên máy local
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['webbanhang1.onrender.com', 'localhost', '127.0.0.1']

LOGIN_REDIRECT_URL = '/'

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Giao diện Admin đẹp (phải đặt đầu tiên)
    'cloudinary_storage', # Quản lý lưu trữ ảnh
    'cloudinary',         # Thư viện Cloudinary
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app', # Tên app của bạn
    'widget_tweaks',
    'django_cleanup.apps.CleanupConfig',
    'rest_framework', 
    'rest_framework_simplejwt', 
    'allauth', 
    'allauth.account',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # QUAN TRỌNG: Để hiển thị CSS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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
                'app.context_processors.cart_context', # Context giỏ hàng
            ],
        },
    },
]

WSGI_APPLICATION = 'webbanhang.wsgi.application'

# Database
# Lưu ý: Thông tin này đang lộ mật khẩu, nên bảo mật kỹ hơn trong tương lai
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.vnymenleyclysclxnljj', 
        'PASSWORD': 'sueu5svcnLBSSiA0',
        'HOST': 'aws-1-ap-southeast-1.pooler.supabase.com',
        'PORT': '6543',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Cấu hình Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dhtqwmp9f', 
    'API_KEY': '445756636998613',     
    'API_SECRET': 'L-4Ds71mVU6SL9y3z1-_Od1_Zto'   
}

# Media settings
MEDIA_URL = '/media/'

# CẤU HÌNH LƯU TRỮ (QUAN TRỌNG NHẤT)
# Đây là cấu hình chuẩn cho Django 4.2 trở lên để xử lý cả Static và Media
STORAGES = {
    "default": {
        # Dùng Cloudinary để lưu ảnh upload
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        # Dùng WhiteNoise để nén và phục vụ file CSS/JS
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Fix lỗi WhiteNoise nếu thiếu file trong manifest
WHITENOISE_MANIFEST_STRICT = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'