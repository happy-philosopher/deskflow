# Регистрируйте свои модели здесь


from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Desk


@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ("number", "employee", "extra_info_preview")
    search_fields = (
        "number",
        "extra_info",
        "employee__first_name",
        "employee__last_name",
    )
    list_filter = ("employee",)

    @admin.display(description=_("доп. информация (фрагмент)"))
    def extra_info_preview(self, obj):
        text = (obj.extra_info or "").strip()
        if not text:
            return "-"
        return text[:60] + ("…" if len(text) > 60 else "")
