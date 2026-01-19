import pytest
from src.storage import JsonSaver
from src.models import Vacancy
import json
from pathlib import Path


# Мок для временного файла
@pytest.fixture
def temp_json_file(tmpdir):
    filepath = Path(tmpdir.mkdir("data")).joinpath("vacancies.json")
    return filepath


# Тестирование read_data
def test_read_data(temp_json_file):
    # Создаем тестовый файл
    test_data = [
        {"name": "Test",
         "url": "test_url",
         "work_format": ["Remote"],
         "salary_from": 100,
         "salary_to": 200}
    ]
    with open(temp_json_file, "w") as f:
        json.dump(test_data, f)

    saver = JsonSaver(str(temp_json_file))
    vacancies = saver.read_data()
    assert len(vacancies) == 1
    assert vacancies[0].name == "Test"


# Тестирование add_data
def test_add_data(temp_json_file):
    saver = JsonSaver(str(temp_json_file))
    vacancy = Vacancy("Test", "test_url", ["Remote"], 100, 200)
    result = saver.add_data([vacancy])
    assert result is True

    # Проверяем, что данные сохранились
    with open(temp_json_file, "r") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["name"] == "Test"


# Тестирование delete_data
def test_delete_data(temp_json_file):
    # Инициализация и добавление данных
    saver = JsonSaver(str(temp_json_file))
    vacancy = Vacancy("Test", "test_url", ["Remote"], 100, 200)
    saver.add_data([vacancy])

    # Удаление
    result = saver.delete_data("test_url")
    assert result is True

    # Проверка удаления
    data = saver.read_data()
    assert len(data) == 0


# Тестирование обработки ошибок
def test_read_data_errors():
    saver = JsonSaver("nonexistent_file.json")
    vacancies = saver.read_data()
    assert len(vacancies) == 0  # Должен возвращать пустой список при ошибке
