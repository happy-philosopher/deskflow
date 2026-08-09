from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from .models import EmployeeProfile


class HomeView(ListView):
    model = EmployeeProfile
    template_name = "home.html"
    context_object_name = "employees"
    queryset = EmployeeProfile.objects.prefetch_related("skills", "images", "employee_skills__skill") \
                                       .select_related("desk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_employees'] = EmployeeProfile.objects.count()
        latest_employees = (
            EmployeeProfile.objects
            .select_related('desk')
            .prefetch_related('images', 'employee_skills__skill')
            .order_by('-hire_date')[:4]
        )
        context['latest_employees'] = latest_employees
        return context


class EmployeeListView(ListView):
    model = EmployeeProfile
    template_name = "employees/employee_list.html"
    context_object_name = "object_list"
    paginate_by = 10

    def get_queryset(self):
        return (
            EmployeeProfile.objects
            .select_related('desk')
            .prefetch_related('images', 'employee_skills__skill')
            .order_by('-hire_date')
        )


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = "employees/employee_detail.html"
    login_url = "/login/"
    context_object_name = "employee"

    def get_queryset(self):
        return super().get_queryset().select_related('desk') \
                                      .prefetch_related('images', 'employee_skills__skill')
