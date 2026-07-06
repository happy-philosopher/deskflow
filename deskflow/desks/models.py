# Создавайте свои модели здесь


from django.db import models
from django.utils.translation import gettext_lazy as _

from employees.models import EmployeeProfile


class Desk(models.Model):
    """Рабочее место (стол) сотрудника."""

    number = models.CharField(
        _("номер стола"),
        max_length=20,
        unique=True,
        help_text=_("например, A12, 305, B-02"),
    )
    extra_info = models.TextField(
        _("дополнительная информация"),
        blank=True,
        help_text=_("любые примечания по рабочему месту"),
    )
    employee = models.OneToOneField(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="desk",
        verbose_name=_("закреплённый сотрудник"),
    )

    created_at = models.DateTimeField(_("дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("дата обновления"), auto_now=True)

    class Meta:
        verbose_name = _("рабочее место")
        verbose_name_plural = _("рабочие места")
        ordering = ["number"]

    def __str__(self) -> str:
        base = f"Стол {self.number}"
        if self.employee:
            return f"{base} ({self.employee})"
        return base
