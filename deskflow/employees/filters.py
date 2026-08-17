import django_filters
from django.utils import timezone
from .models import EmployeeProfile


class EmployeeFilter(django_filters.FilterSet):
    # Фильтр по навыкам (поиск по названию)
    skills = django_filters.CharFilter(
        field_name='skills__name',
        lookup_expr='icontains',
        label='Навыки'
    )

    # Фильтр по минимальному стажу (дней)
    min_experience = django_filters.NumberFilter(
        method='filter_min_experience',
        label='Стаж (мин., дней)'
    )

    # Фильтр по максимальному стажу (дней)
    max_experience = django_filters.NumberFilter(
        method='filter_max_experience',
        label='Стаж (макс., дней)'
    )

    def filter_min_experience(self, queryset, name, value):
        if value is not None:
            try:
                days = int(value)  # преобразуем в int
            except (ValueError, TypeError):
                return queryset
            limit_date = timezone.now().date() - timezone.timedelta(days=days)
            return queryset.filter(hire_date__lte=limit_date)
        return queryset

    def filter_max_experience(self, queryset, name, value):
        if value is not None:
            try:
                days = int(value)  # преобразуем в int
            except (ValueError, TypeError):
                return queryset
            limit_date = timezone.now().date() - timezone.timedelta(days=days)
            return queryset.filter(hire_date__gte=limit_date)
        return queryset

    class Meta:
        model = EmployeeProfile
        fields = ['skills', 'min_experience', 'max_experience']
