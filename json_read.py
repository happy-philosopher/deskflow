import json
from pathlib import Path


def read_and_print_json(file_path: str):
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        print(f"❌ Файл не найден: {path}")
        return
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ JSON успешно загружен.\n")
        print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка формата JSON: {e}")
    except PermissionError:
        print(f"❌ Нет прав на чтение файла: {path}")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")


if __name__ == "__main__":
    user_input = input("Путь к JSON-файлу: ").strip().strip('"')
    read_and_print_json(user_input)
