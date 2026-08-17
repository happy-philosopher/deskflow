from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .validators import validate_hire_date
from .models import EmployeeProfile, EmployeeSkill, Skill, EmployeeImage


class EmployeeImageInline(admin.TabularInline):
    model = EmployeeImage
    extra = 1  # количество пустых форм для добавления
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

    list_display = ("first_name", "last_name", "middle_name", "gender", "user", "hire_date")
    list_filter = ("gender",)
    search_fields = ("first_name", "last_name", "middle_name", "user__username")

    # Добавляем инлайн для изображений
    inlines = [EmployeeSkillInline, EmployeeImageInline]

    fieldsets = [
        (None, {
            'fields': ['user', 'first_name', 'last_name', 'middle_name', 'gender', 'hire_date']
        }),
        (_('Описание'), {
            'fields': ['description']
        }),
    ]

    def clean(self):
        super().clean()
        if self.hire_date:
            validate_hire_date(self.hire_date)

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js')


class CustomUserAdmin(UserAdmin):
    def get_groups(self, obj):
        """Возвращает список групп пользователя через запятую."""
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Группы'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Вставляем 'get_groups' после 'username' в list_display
        base_list = list(self.list_display)
        if 'username' in base_list:
            idx = base_list.index('username')
            if 'get_groups' in base_list:
                base_list.remove('get_groups')
            base_list.insert(idx + 1, 'get_groups')
        else:
            if 'get_groups' not in base_list:
                base_list.append('get_groups')
        self.list_display = tuple(base_list)

# Перерегистрируем модель User с кастомным админом
admin.site.unregister(User)  # если уже зарегистрирована
admin.site.register(User, CustomUserAdmin)
