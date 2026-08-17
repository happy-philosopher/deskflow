from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import EmployeeProfileSerializer
from .filters import EmployeeFilter
from .permissions import IsAdmin, IsWardenOrAdmin
from .models import EmployeeProfile, EmployeeImage, EmployeeSkill
from desks.models import Desk


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


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['first_name', 'last_name', 'middle_name']
    ordering_fields = ['hire_date', 'first_name', 'last_name']
    ordering = ['-hire_date']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['patch'], permission_classes=[IsWardenOrAdmin])
    def move(self, request, pk=None):
        employee = self.get_object()
        desk_id = request.data.get('desk')
        if desk_id is None:
            return Response({'error': 'Поле "desk" обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            desk = Desk.objects.get(pk=desk_id)
        except Desk.DoesNotExist:
            return Response({'error': 'Стол не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Проверка соседства выполняется в модели через full_clean()
        employee.desk = desk
        try:
            employee.full_clean()
            employee.save()
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(employee)
        return Response(serializer.data)
