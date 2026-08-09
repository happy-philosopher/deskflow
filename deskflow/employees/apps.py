from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"
    verbose_name = "сотрудники"

    def ready(self):
        try:
            from . import signals
        except ImportError:
            pass
