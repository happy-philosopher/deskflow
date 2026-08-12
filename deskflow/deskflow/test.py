from pathlib import Path

print()

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)

STATICFILES_DIRS = [
    BASE_DIR / 'static_dev',
]
print(STATICFILES_DIRS)