# Приложение DeskFlow
## Структура приложения

```
deskflow/
├── deskflow/
│    ├── deskflow/
│    │    ├── __init__.py
│    │    ├── asgi.py
│    │    ├── settings.py
│    │    ├── urls.py
│    │    └── wsgi.py
│    │
│    ├── desks/
│    │    ├── migrations/
│    │    │    └── ...
│    │    ├── __init__.py
│    │    ├── admin.py
│    │    ├── apps.py
│    │    ├── models.py
│    │    ├── tests.py
│    │    └── wiews.py
│    │
│    ├── employees/
│    │    ├── migrations/
│    │    │    └── ...
│    │    ├── __init__.py
│    │    ├── admin.py
│    │    ├── apps.py
│    │    ├── models.py
│    │    ├── tests.py
│    │    └── wiews.py
│    │
│    ├── static_dev/
│    │    ├── css/
│    │    │    └── style.css
│    │    │
│    │    ├── img/
│    │    │    └── ...
│    │    │
│    │    └── js/
│    │         └── ...
│    │
│    ├── media/
│    │    └── photos/
│    │         └── ...
│    │
│    ├── templates/
│    │    ├── desks/
│    │    │    └── ...
│    │    │
│    │    ├── employees/
│    │    │    ├── employee_list.html
│    │    │    ├── employee_detail.html
│    │    │    └── _employee_card.html  # частичный шаблон (карточка сотрудника)
│    │    │
│    │    ├── base.html
│    │    ├── home.html
│    │    ├── header.html
│    │    └── footer.html
│    │
│    ├── db.sqlite3
│    ├── manage.py
│    └── models.png
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Запуск приложения
```
...\deskflow\deskflow> python manage.py runserver
```

## Тестирование приложения
```
...\deskflow\deskflow> python manage.py test
```
