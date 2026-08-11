from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
from django.utils import timezone

from .models import EmployeeProfile, EmployeeImage, EmployeeSkill


class HomeView(ListView):
    model = EmployeeProfile
    template_name = "home.html"
    context_object_name = "employees"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_employees'] = EmployeeProfile.objects.count()

        latest_employees = (
            EmployeeProfile.objects
            .prefetch_related(
                'skills',
                Prefetch(
                    'images',
                    queryset=EmployeeImage.objects.order_by('order'),
                    to_attr='prefetched_images'
                )
            )
            .order_by('-hire_date')[:4]
        )

        for emp in latest_employees:
            emp.first_image = emp.prefetched_images[0] if emp.prefetched_images else None

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
            .prefetch_related(
                'skills',
                Prefetch(
                    'images',
                    queryset=EmployeeImage.objects.order_by('order'),
                    to_attr='prefetched_images'
                )
            )
            .order_by('-hire_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for emp in context['object_list']:
            emp.first_image = emp.prefetched_images[0] if emp.prefetched_images else None
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = "employees/employee_detail.html"
    login_url = "/login/"
    context_object_name = "employee"

    def get_queryset(self):
        return super().get_queryset().select_related('desk') \
            .prefetch_related(
                Prefetch(
                    'images',
                    queryset=EmployeeImage.objects.order_by('order'),
                    to_attr='prefetched_images'
                ),
                Prefetch(
                    'employee_skills',
                    queryset=EmployeeSkill.objects.select_related('skill').order_by('skill__name'),
                    to_attr='prefetched_employee_skills'
                )
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object

        prefetched_images = getattr(employee, 'prefetched_images', [])
        context['main_image'] = prefetched_images[0] if prefetched_images else None
        context['other_images'] = prefetched_images[1:] if len(prefetched_images) > 1 else []
        context['skills_with_levels'] = getattr(employee, 'prefetched_employee_skills', [])
        context['experience_days'] = (timezone.now().date() - employee.hire_date).days if employee.hire_date else 0

        # Безопасное получение номера стола (если есть)
        if hasattr(employee, 'desk') and employee.desk:
            context['desk_number'] = employee.desk.number
        else:
            context['desk_number'] = None

        return context
