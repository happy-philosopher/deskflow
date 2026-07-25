# Создавайте свои представления здесь.


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from .models import EmployeeProfile


class HomeView(ListView):
    model = EmployeeProfile
    template_name = "home.html"
    context_object_name = "employees"
    queryset = EmployeeProfile.objects.prefetch_related("skills")  # оптимизация запросов


class EmployeeListView(ListView):
    model = EmployeeProfile
    template_name = "employees/employee_list.html"
    context_object_name = "object_list"
    queryset = EmployeeProfile.objects.prefetch_related("skills")


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = "employees/employee_detail.html"
    login_url = "/login/"  # перенаправление на страницу входа
    context_object_name = "employee"  # явно указываем имя контекста

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Получаем навыки с уровнями, отсортированные по названию навыка
        obj.skills_with_levels = obj.employee_skills.order_by("skill__name")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = context["employee"]

        # Сортируем фотографии по полю order и передаём в шаблон
        context["employee_images"] = employee.images.all().order_by("order")
        return context
