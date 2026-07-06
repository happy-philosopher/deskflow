# Регистрируйте свои модели здесь


from django.contrib import admin

from .models import EmployeeProfile, EmployeeSkill, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1
    min_num = 0


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "middle_name", "gender", "user")
    list_filter = ("gender",)
    search_fields = ("first_name", "last_name", "middle_name", "user__username")
    inlines = [EmployeeSkillInline]
