import pytest
from typing import List, Optional
from src.models import Vacancy

def test_vacancy_init_with_none_values():
    """Проверяет обработку None-значений внутри __init__."""
    name: Optional[str] = None
    url: Optional[str] = None
    work_format: Optional[List[str]] = None

    vacancy = Vacancy(
        name=name,
        url=url,
        work_format=work_format,
        salary_from=None,  # Передаём None, а не -1
        salary_to=None
    )

    assert vacancy.name == "Без названия"
    assert vacancy.url == ""
    assert vacancy.work_format == ["Не указано"]
    assert vacancy.salary_from == 0  # None → 0
    assert vacancy.salary_to == 0     # None → 0

@pytest.mark.parametrize(
    "salary_from, salary_to, expected",
    [
        (0, 0, "не указана"),
        (10000, 0, "от 10000 руб."),
        (0, 20000, "до 20000 руб."),
        (10000, 20000, "от 10000 до 20000 руб."),
        (15000, 15000, "15000 руб."),
    ]
)
def test_format_salary(salary_from, salary_to, expected):
    """Проверяет форматирование строки зарплаты."""
    vacancy = Vacancy(
        "Test",
        "url",
        ["Remote"],
        salary_from, salary_to
    )
    assert vacancy._format_salary() == expected

def test_cast_to_object_list():
    """Проверяет преобразование списка словарей
     в список объектов Vacancy."""
    vacancy_list = [
        {
            "name": "Dev1",
            "alternate_url": "url1",
            "salary": {
                "from": 100,
                "to": 200,
                "currency": "RUB"
            }
        },
        {
            "name": "Dev2",
            "alternate_url": "url2",
            "salary": {"from": 300, "to": 400, "currency": "RUB"}
        }
    ]
    vacancies = Vacancy.cast_to_object_list(vacancy_list)

    assert len(vacancies) == 2
    assert all(isinstance(v, Vacancy) for v in vacancies)

    assert vacancies[0].name == "Dev1"
    assert vacancies[0].url == "url1"
    assert vacancies[0].salary_from == 100
    assert vacancies[0].salary_to == 200

    assert vacancies[1].name == "Dev2"
    assert vacancies[1].url == "url2"
    assert vacancies[1].salary_from == 300
    assert vacancies[1].salary_to == 400

def test_created_vacancy():
    """Проверяет создание вакансии из словаря (HH API)."""
    vacancy_data = {
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/123",
        "schedule": {"name": "Full-time"},
        "employment": {"name": "Permanent"},
        "salary": {
            "from": 100000,
            "to": 150000,
            "currency": "RUB"}
    }
    vacancy = Vacancy.created_vacancy(vacancy_data)

    assert isinstance(vacancy, Vacancy)
    assert vacancy.name == "Python Developer"
    assert vacancy.url == "https://hh.ru/vacancy/123"
    assert "Full-time" in vacancy.work_format
    assert "Permanent" in vacancy.work_format
    assert vacancy.salary_from == 100000
    assert vacancy.salary_to == 150000

def test_medium_salary():
    """Проверяет расчёт средней зарплаты."""
    assert Vacancy(
        "T",
        "u",
        [],
        10000,
        20000
    ).medium_salary() == 15000.0
    assert Vacancy(
        "T",
        "u",
        [],
        0,
        0
    ).medium_salary() == 0.0
    assert Vacancy(
        "T",
        "u",
        [],
        5000,
        0
    ).medium_salary() == 5000.0
    assert Vacancy(
        "T",
        "u",
        [],
        0,
        8000
    ).medium_salary() == 8000.0


def test_has_salary():
    """Проверяет наличие зарплаты."""
    assert Vacancy(
        "T",
        "u",
        [],
        10000,
        20000
    ).has_salary() is True
    assert Vacancy(
        "T",
        "u",
        [],
        5000,
        0
    ).has_salary() is True
    assert Vacancy(
        "T",
        "u",
        [],
        0,
        0
    ).has_salary() is False
