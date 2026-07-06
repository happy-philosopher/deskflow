# Создавайте свои модели здесь


from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class Skill(models.Model):
    name = models.CharField(
        _("название навыка"),
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = _("навык")
        verbose_name_plural = _("навыки")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class EmployeeProfile(models.Model):
    GENDER_CHOICES = [
        ("M", _("Мужской")),
        ("F", _("Женский")),
        ("O", _("Другой")),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name=_("пользователь"),
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
