"""
Django settings for webbanhang project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#&t(x&a6$w9o*q#n2so6(niikk5__7dmdpfj7g6&5k%_7*3af&')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['webbanhang1.onrender.com', 'localhost', '127.0.0.1']

LOGIN_REDIRECT_URL = '/'

# Application definition
INSTALLED_APPS = [
    # 1. Giao diện Admin (Phải đặt đầu tiên để override template gốc)
    'jazzmin',

    # 2. Các ứng dụng lõi của Django (Nên load trước các thư viện bên thứ 3)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # <--- Quan trọng: Phải đứng trước Cloudinary

    # 3. Các thư viện bên thứ 3 (Di chuyển Cloudinary xuống đây)
    'cloudinary_storage',
    'cloudinary',
    'widget_tweaks',
    'django_cleanup.apps.CleanupConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'allauth',
    'allauth.account',
    'crispy_forms',
    # 'crispy_bootstrap5', # (Nếu bạn có cài gói này thì nên thêm vào đây)

    # 4. App của dự án
    'app',
    'django.contrib.humanize',  
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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.tcytdxhscmhxxevyvtjg',
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

# CẤU HÌNH LƯU TRỮ
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

# Fix lỗi WhiteNoise nếu thiếu file trong manifest
WHITENOISE_MANIFEST_STRICT = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Fix lỗi AttributeError cho thư viện cũ
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"