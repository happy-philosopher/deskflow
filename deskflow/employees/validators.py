# employees/validators.py


import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.apps import apps


# Словарь транслитерации русских букв в латинские (заглавные)
TRANSLIT_MAP = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
    'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
}


def normalize_letter(letter):
    """Приводит букву к латинскому эквиваленту (заглавную)."""
    upper_letter = letter.upper()
    return TRANSLIT_MAP.get(upper_letter, upper_letter)


def validate_desk_exists(desk_id):
    from desks.models import Desk
    if not Desk.objects.filter(id=desk_id).exists():
        raise ValidationError("Такого стола нет")


def validate_desk_adjacency(desk):
    """
    Проверяет, что за соседними столами (в одном ряду) не сидят
    тестировщик и программист одновременно.
    """
    if not desk.employee:
        return

    employee = desk.employee
    from desks.models import Desk
    current_type = employee.get_employee_type()
    if current_type not in ('tester', 'developer'):
        return

    # Разбираем номер стола
    match = re.match(r'([A-Za-zА-Яа-я]+)(\d+)', desk.number)
    if match:
        # Буквенно-цифровой номер
        letter = match.group(1)
        try:
            number = int(match.group(2))
        except ValueError:
            return
        normalized_letter = normalize_letter(letter)

        # Получаем все столы, кроме текущего
        all_desks = Desk.objects.exclude(pk=desk.pk)

        for other_desk in all_desks:
            if not other_desk.employee:
                continue
            other_match = re.match(r'([A-Za-zА-Яа-я]+)(\d+)', other_desk.number)
            if not other_match:
                continue
            other_letter = other_match.group(1)
            try:
                other_number = int(other_match.group(2))
            except ValueError:
                continue
            other_normalized = normalize_letter(other_letter)
            if normalized_letter == other_normalized and abs(other_number - number) == 1:
                neighbor_type = other_desk.employee.get_employee_type()
                if (current_type == 'tester' and neighbor_type == 'developer') or \
                        (current_type == 'developer' and neighbor_type == 'tester'):
                    raise ValidationError(
                        _("Нельзя сажать тестировщика и программиста за соседние столы (в одном ряду).")
                    )
    else:
        # Числовой номер (только цифры)
        try:
            number = int(desk.number)
        except ValueError:
            return

        all_desks = Desk.objects.exclude(pk=desk.pk)
        for other_desk in all_desks:
            if not other_desk.employee:
                continue
            # Проверяем, что номер соседа тоже числовой
            if not re.match(r'^\d+$', other_desk.number):
                continue
            try:
                other_number = int(other_desk.number)
            except ValueError:
                continue
            if abs(other_number - number) == 1:
                neighbor_type = other_desk.employee.get_employee_type()
                if (current_type == 'tester' and neighbor_type == 'developer') or \
                        (current_type == 'developer' and neighbor_type == 'tester'):
                    raise ValidationError(
                        _("Нельзя сажать тестировщика и программиста за соседние столы (в одном ряду).")
                    )


def validate_hire_date(date):
    if date and date > timezone.now().date():
        raise ValidationError(
            _('Дата приёма не может быть в будущем'),
            code='invalid_date'
        )
