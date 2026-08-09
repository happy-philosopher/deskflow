# employees/models.py
# Создавайте свои модели здесь


from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from .validators import validate_hire_date
from django.core.exceptions import ValidationError
from django.utils import timezone


class Skill(models.Model):
    name = models.CharField(
        _("название навыка"),
        max_length=100,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("навык")
        verbose_name_plural = _("навыки")
        ordering = ["name"]


class EmployeeProfile(models.Model):
    GENDER_CHOICES = [
        ("M", _("Мужской")),
        ("F", _("Женский")),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="employee_profile",
        verbose_name=_("пользователь"),
        blank=True,
        null=True,
        help_text=_("необязательно"),
    )

    first_name = models.CharField(_("имя"), max_length=50)

    last_name = models.CharField(_("фамилия"), max_length=50)

    middle_name = models.CharField(
        _("отчество"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("необязательно"),
    )

    gender = models.CharField(
        _("пол"),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    description = CKEditor5Field(
        config_name="extends",
        verbose_name=_("описание"),
        blank=True,
        help_text=_("WYSIWYG-редактор (Django ckeditor 5)"),
    )

    skills = models.ManyToManyField(
        Skill,
        through="EmployeeSkill",
        related_name="employees",
        verbose_name=_("навыки"),
    )

    hire_date = models.DateField(
        _("дата приёма на работу"),
        null=True,
        blank=True,
        validators=[validate_hire_date]
    )

    created_at = models.DateTimeField(_("дата создания"), auto_now_add=True)

    updated_at = models.DateTimeField(_("дата обновления"), auto_now=True)

    class Meta:
        verbose_name = _("профиль сотрудника")
        verbose_name_plural = _("профили сотрудников")

    def __str__(self) -> str:
        parts = [self.first_name, self.last_name]
        if self.middle_name:
            parts.insert(1, self.middle_name)
        return " ".join(parts)

    def get_employee_type(self) -> str:
        """Определяет тип сотрудника: тестировщик, разработчик или другой"""

        print(f"get_employee_type для {self} вызван")
        # Проверка на тестировщика
        tester_skill = Skill.objects.filter(name="Знание QA/тестирования").first()
        if tester_skill and self.employee_skills.filter(skill=tester_skill, level__gte=6, level__lte=10).exists():
            print("Результат: tester")
            return 'tester'

        # Проверка на разработчика
        if self.employee_skills.filter(skill__name__icontains="Программирование", level__gte=6, level__lte=10).exists():
            print("Результат: developer")
            return 'developer'

        print("Результат: other")
        return 'other'

    def save(self, *args, **kwargs):
        # Валидация будет вызываться из отдельного файла
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.hire_date and self.hire_date > timezone.now().date():
            raise ValidationError({'hire_date': _('Дата приёма не может быть в будущем')})

    @property
    def main_image(self):
        """Первое изображение (по порядку)"""
        return self.images.order_by('order').first()

    @property
    def other_images(self):
        """Все изображения, кроме первого"""
        return self.images.order_by('order')[1:]

    @property
    def desk_number(self):
        """Номер стола (если привязан)"""
        return self.desk.number if hasattr(self, 'desk') and self.desk else None

    @property
    def experience_days(self):
        """Стаж в днях от даты приёма до сегодня"""
        if self.hire_date:
            return (timezone.now().date() - self.hire_date).days
        return 0

    @property
    def skills_with_levels(self):
        """Навыки с уровнями (через промежуточную модель)"""
        return self.employee_skills.select_related('skill').order_by('skill__name')


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="employee_skills",
        verbose_name=_("сотрудник"),
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="employee_skills",
        verbose_name=_("навык"),
    )

    level = models.PositiveSmallIntegerField(
        _("уровень освоения"),
        default=1,
        help_text=_("от 1 до 10"),
    )

    class Meta:
        verbose_name = _("уровень навыка сотрудника")
        verbose_name_plural = _("уровни навыков сотрудников")
        unique_together = ("employee", "skill")
        constraints = [
            models.CheckConstraint(
                check=models.Q(level__gte=1) & models.Q(level__lte=10),
                name="level_between_1_and_10",
            )
        ]

    def __str__(self) -> str:
        return f"{self.employee} — {self.skill}: {self.level}"


class EmployeeImage(models.Model):
    image = models.ImageField(upload_to="employees/", verbose_name="изображение")

    order = models.IntegerField(verbose_name="порядок")

    employee = models.ForeignKey(
        EmployeeProfile, related_name="images", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.employee} — изображение №{self.order}"

    def delete(self, *args, **kwargs):
        try:
            # Проверяем существование файла перед удалением
            if self.image and self.image.name:
                self.image.delete(save=False)  # удаляем файл с диска
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
        finally:
            super().delete(*args, **kwargs)  # удаляем запись из БД

    class Meta:
        ordering = ["order"]
