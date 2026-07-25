# Регистрируйте свои модели здесь


from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _

from .models import EmployeeProfile, EmployeeSkill, Skill, EmployeeImage


class EmployeeImageInline(admin.TabularInline):
    model = EmployeeImage
    extra = 3  # количество пустых форм для добавления
    readonly_fields = ['image_preview']  # добавим превью

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100">'
        return '(нет изображения)'

    image_preview.short_description = 'Превью'
    image_preview.allow_tags = True


class EmployeeResource(resources.ModelResource):
    class Meta:
        model = EmployeeProfile


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1
    min_num = 0


# Одна регистрация: совмещаем импорт/экспорт + инлайны + настройки отображения
@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource

    list_display = ("first_name", "last_name", "middle_name", "gender", "user")
    list_filter = ("gender",)
    search_fields = ("first_name", "last_name", "middle_name", "user__username")

    # Добавляем инлайн для изображений
    inlines = [EmployeeSkillInline, EmployeeImageInline]  # теперь здесь два инлайна

    fieldsets = [
        (None, {
            'fields': ['user', 'first_name', 'last_name', 'middle_name', 'gender']
        }),
        (_('Описание'), {
            'fields': ['description']
        }),
    ]

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js')
