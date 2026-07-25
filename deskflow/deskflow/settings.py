"""
Настройки Django для проекта deskflow.

Сгенерированы "django-admin startproject" с использованием Django 5.2.

Для получения дополнительной информации об этом файле смотрите:
https://docs.djangoproject.com/en/5.2/topics/settings/

Полный список настроек и их значений приведен в разделе:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path
from import_export.formats.base_formats import CSV, JSON


BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0=86d^_94fk+cfv8dhyudbf8am@uj00dbx5z_=wuv9n!nvq7ax'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INTERNAL_IPS = [
    '127.0.0.1',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения
    'debug_toolbar',
    'django_ckeditor_5',  # Встраиваемый редактор
    'django_extensions',
    'import_export',

    # Мои приложения
    'employees',
    'desks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # В самый конец списка
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'deskflow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'deskflow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


# Статические файлы (CSS, JS, общие изображения)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static_dev',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # для сбора при деплое


# Медиа-файлы (пользовательские фото)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Настройки для CKEditor 5 ---
CKEDITOR_5_CONFIGS = {
    'extends': {
        # Настройка панели инструментов (toolbar)
        'toolbar': {
            'toolbar_panel_id': 'toolbar',  # ID панели
            'toolbar_width': '100%',      # Ширина панели
            'items': [
                'undo', 'redo', '|',  # Кнопки undo/redo и разделитель
                'heading', '|',         # Заголовки
                'bold', 'italic', 'underline', 'strikethrough', '|',  # Шрифтовое оформление
                'alignment', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',  # Текст и шрифт
                'link', 'imageUpload', 'mediaEmbed', 'fileUpload', '|',  # Медиа и ссылки
                'bulletedList', 'numberedList', 'todoList', '|',  # Списки
                'blockQuote', 'insertTable', 'codeBlock', 'code', '|',  # Таблицы и код
                'findAndReplace', 'highlight', 'removeFormat'
            ],
            'shouldNotGroupWhenFull': True  # Не группировать кнопки, когда панель заполнена
        },

        # Язык редактора
        'language': 'ru',

        # Настройки для плагина image
        'image': {
            'toolbar': [
                'imageTextAlternative',  # Альтернативный текст для изображения
                'imageStyle:full',      # Стиль изображения (full, side)
                'imageStyle:side'       # Стиль сбоку
            ]
        },

        # Настройки для плагина table
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells']  # Кнопки для работы с таблицей
        },

        # Заполнитель (плейсхолдер) в редакторе
        'placeholder': 'Введите текст...',

        # Дополнительные опции (можно расширять под свои нужды)
        'link': {
            'target': '_blank'  # Открывать ссылку в новом окне
        },
        'mediaEmbed': {
            'previewsInData': True  # Показывать превью ссылок (например, видео YouTube)
        },
    }
}


# Настройки import-export
IMPORT_FORMATS = [JSON]
EXPORT_FORMATS = [JSON]
