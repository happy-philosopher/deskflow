# Тесты /employees/tests.py


from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import EmployeeProfile, EmployeeSkill, Skill
from desks.models import Desk


class BaseTestMixin:
    """Миксин с вспомогательными методами для создания тестовых данных."""

    def create_user(self, username='testuser', password='testpass'):
        User = get_user_model()
        return User.objects.create_user(username=username, password=password)

    def create_employee(self, user=None, first_name='Иван', last_name='Иванов',
                        hire_date=None, **kwargs):
        if hire_date is None:
            hire_date = timezone.now().date() - timezone.timedelta(days=30)
        return EmployeeProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            hire_date=hire_date,
            **kwargs
        )

    def create_skill(self, name):
        # Используем get_or_create для избежания дублирования
        skill, _ = Skill.objects.get_or_create(name=name)
        return skill

    def create_employee_skill(self, employee, skill, level):
        return EmployeeSkill.objects.create(employee=employee, skill=skill, level=level)

    def create_desk(self, number, employee=None):
        return Desk.objects.create(number=number, employee=employee)

    def create_employee_with_type(self, emp_type, first_name, last_name):
        """
        Создаёт сотрудника с типом 'developer' или 'tester'.
        Для разработчика: навык "Программирование на Python" уровень 10.
        Для тестировщика: навык "Знание QA/тестирования" уровень 10,
        и программирование на уровне 5 (чтобы не стать разработчиком).
        """
        employee = self.create_employee(first_name=first_name, last_name=last_name)

        if emp_type == 'developer':
            skill = self.create_skill('Программирование на Python')
            self.create_employee_skill(employee, skill, 10)
        elif emp_type == 'tester':
            skill_qa = self.create_skill('Знание QA/тестирования')
            self.create_employee_skill(employee, skill_qa, 10)
            skill_prog = self.create_skill('Программирование на JavaScript')
            self.create_employee_skill(employee, skill_prog, 5)
        return employee


class HomePageTests(TestCase, BaseTestMixin):
    """Тесты главной страницы."""

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_context(self):
        for i in range(5):
            self.create_employee(first_name=f'Name{i}', last_name=f'Surname{i}')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_employees'], 5)
        latest = response.context['latest_employees']
        self.assertEqual(len(latest), 4)
        dates = [emp.hire_date for emp in latest]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')


class EmployeeListPageTests(TestCase, BaseTestMixin):
    """Тесты страницы списка сотрудников."""

    def test_employee_list_status_code(self):
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)

    def test_employee_list_context(self):
        for i in range(15):
            self.create_employee(first_name=f'Name{i}', last_name=f'Surname{i}')
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 10)
        self.assertIn('paginator', response.context)
        self.assertEqual(response.context['paginator'].num_pages, 2)

        response2 = self.client.get(reverse('employee_list') + '?page=2')
        self.assertEqual(len(response2.context['object_list']), 5)

    def test_employee_list_uses_correct_template(self):
        response = self.client.get(reverse('employee_list'))
        self.assertTemplateUsed(response, 'employees/employee_list.html')


class EmployeeDetailPageTests(TestCase, BaseTestMixin):
    """Тесты детальной страницы сотрудника (требует авторизации)."""

    def setUp(self):
        self.user = self.create_user()
        self.employee = self.create_employee(
            user=self.user,
            first_name='Тест',
            last_name='Тестов'
        )
        self.detail_url = reverse('employee_detail', kwargs={'pk': self.employee.pk})

    def test_detail_page_redirects_anonymous(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что редирект содержит '?next=' и путь к детальной странице
        self.assertIn('?next=', response.url)
        self.assertIn(self.detail_url, response.url)

    def test_detail_page_accessible_for_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_detail_page_context(self):
        self.client.force_login(self.user)
        skill = self.create_skill('Python')
        self.create_employee_skill(self.employee, skill, 7)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('main_image', response.context)
        self.assertIn('other_images', response.context)
        self.assertIn('skills_with_levels', response.context)
        self.assertIn('experience_days', response.context)
        self.assertIn('desk_number', response.context)

        skills_with_levels = response.context['skills_with_levels']
        self.assertEqual(len(skills_with_levels), 1)
        self.assertEqual(skills_with_levels[0].skill.name, 'Python')
        self.assertEqual(skills_with_levels[0].level, 7)
        self.assertGreaterEqual(response.context['experience_days'], 0)
        self.assertIsNone(response.context['desk_number'])

    def test_detail_page_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url)
        self.assertTemplateUsed(response, 'employees/employee_detail.html')


class DeskAdjacencyValidatorTest(TestCase, BaseTestMixin):
    """Тест валидатора, запрещающего соседство разработчика и тестировщика."""

    def test_adjacency_validation_blocks_developer_and_tester(self):
        developer = self.create_employee_with_type('developer', 'Михаил', 'Иванов')
        tester = self.create_employee_with_type('tester', 'Алёна', 'Королёва')

        desk1 = self.create_desk('A1', developer)
        desk1.full_clean()
        desk1.save()

        desk2 = self.create_desk('A2')
        desk2.employee = tester
        with self.assertRaises(ValidationError) as cm:
            desk2.full_clean()
        self.assertIn('Нельзя сажать тестировщика и программиста', str(cm.exception))

        desk2.refresh_from_db()
        self.assertIsNone(desk2.employee)

    def test_adjacency_allows_same_type(self):
        dev1 = self.create_employee_with_type('developer', 'Петр', 'Петров')
        dev2 = self.create_employee_with_type('developer', 'Сергей', 'Сергеев')

        desk1 = self.create_desk('B1', dev1)
        desk1.full_clean()
        desk1.save()

        desk2 = self.create_desk('B2', dev2)
        desk2.full_clean()
        desk2.save()
        self.assertEqual(desk2.employee, dev2)

    def test_adjacency_ignores_non_adjacent_tables(self):
        developer = self.create_employee_with_type('developer', 'Иван', 'Иванов')
        tester = self.create_employee_with_type('tester', 'Мария', 'Петрова')

        desk1 = self.create_desk('C1', developer)
        desk1.full_clean()
        desk1.save()

        desk2 = self.create_desk('C3', tester)
        desk2.full_clean()
        desk2.save()
        self.assertEqual(desk2.employee, tester)

    def test_adjacency_with_numeric_only_numbers(self):
        developer = self.create_employee_with_type('developer', 'Алексей', 'Смирнов')
        tester = self.create_employee_with_type('tester', 'Елена', 'Кузнецова')

        desk1 = self.create_desk('1', developer)
        desk1.full_clean()
        desk1.save()

        desk2 = self.create_desk('2')
        desk2.employee = tester
        with self.assertRaises(ValidationError):
            desk2.full_clean()

        desk3 = self.create_desk('3', tester)
        desk3.full_clean()
        desk3.save()
        self.assertEqual(desk3.employee, tester)

    def test_adjacency_with_different_letter_rows(self):
        developer = self.create_employee_with_type('developer', 'Дмитрий', 'Дмитриев')
        tester = self.create_employee_with_type('tester', 'Ольга', 'Ольгина')

        desk1 = self.create_desk('A1', developer)
        desk1.full_clean()
        desk1.save()

        desk2 = self.create_desk('B1', tester)
        desk2.full_clean()
        desk2.save()
        self.assertEqual(desk2.employee, tester)
