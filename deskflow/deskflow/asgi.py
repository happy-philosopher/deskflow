"""
Конфигурация ASGI для проекта deskflow.

Она предоставляет возможность вызова ASGI в качестве переменной уровня модуля с именем `application`.

Для получения дополнительной информации об этом файле смотрите:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deskflow.settings')

application = get_asgi_application()
