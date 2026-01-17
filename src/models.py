from typing import Optional, List, Dict, Any


class Vacancy:
    """
    Класс, представляющий вакансию.

    Хранит основную информацию о вакансии: название, URL, зарплатные ожидания,
    формат работы. Поддерживает сравнение вакансий по средней зарплате и преобразование
    в словарь для сериализации.
    """

    name: str
    """Название вакансии (обязательное поле)."""

    url: str
    """URL вакансии (обязательное поле)."""

    salary_from: Optional[int]
    """Минимальная зарплата (в рублях, может быть None)."""

    salary_to: Optional[int]
    """Максимальная зарплата (в рублях, может быть None)."""

    work_format: List[str]
    """Список форматов работы (например, ['Удалённо', 'Гибрид'])."""

    def __init__(
            self,
            name: str,
            url: str,
            work_format: List[str],
            salary_from: Optional[int] = None,
            salary_to: Optional[int] = None
    ):
        """
        Инициализирует объект вакансии.

        :param name: Название вакансии
        :type name: str
        :param url: URL вакансии
        :type url: str
        :param work_format: Список форматов работы
        :type work_format: List[str]
        :param salary_from: Минимальная зарплата (по умолчанию None)
        :type salary_from: Optional[int]
        :param salary_to: Максимальная зарплата (по умолчанию None)
        :type salary_to: Optional[int]

        :raises ValueError: Если name или url пустые
        """
        valid_data = self.validate_vacancies(name, url, salary_from, salary_to)
        self.name = valid_data.get("name")
        self.url = valid_data.get("url")
        self.work_format = work_format
        self.salary_from = valid_data.get("salary_from")
        self.salary_to = valid_data.get("salary_to")

    def __str__(self) -> str:
        """
        Возвращает строковое представление вакансии.

        :return: Форматированная строка с информацией о вакансии
        :rtype: str
        """
        if self.salary_from == 0 and self.salary_to == 0:
            salary_range = "не указано"
        elif self.salary_from == 0:
            salary_range = f"до {self.salary_to}"
        elif self.salary_to == 0:
            salary_range = f"от {self.salary_from}"
        else:
            salary_range = f"от {self.salary_from} до {self.salary_to}"

        result = (
            f"Вакансия {self.name} "
            f"({self.url}), "
            f"зарплата: {salary_range}, "
            f"формат работы: {', '.join(self.work_format)}"
        )
        return result

    def __lt__(self, other: 'Vacancy') -> bool:
        """
        Проверяет, меньше ли средняя зарплата текущей вакансии, чем у другой.

        :param other: Другая вакансия для сравнения
        :type other: Vacancy
        :return: True, если средняя зарплата меньше
        :rtype: bool
        """
        return self.medium_salary() < other.medium_salary()

    def __le__(self, other: 'Vacancy') -> bool:
        """
        Проверяет, меньше или равна ли средняя зарплата текущей вакансии по сравнению с другой.

        :param other: Другая вакансия для сравнения
        :type other: Vacancy
        :return: True, если средняя зарплата меньше или равна
        :rtype: bool
        """
        return self.medium_salary() <= other.medium_salary()

    def __gt__(self, other: 'Vacancy') -> bool:
        """
        Проверяет, больше ли средняя зарплата текущей вакансии, чем у другой.

        :param other: Другая вакансия для сравнения
        :type other: Vacancy
        :return: True, если средняя зарплата больше
        :rtype: bool
        """
        return self.medium_salary() > other.medium_salary()

    def __ge__(self, other: 'Vacancy') -> bool:
        """
        Проверяет, больше или равна ли средняя зарплата текущей вакансии по сравнению с другой.

        :param other: Другая вакансия для сравнения
        :type other: Vacancy
        :return: True, если средняя зарплата больше или равна
        :rtype: bool
        """
        return self.medium_salary() >= other.medium_salary()

    def medium_salary(self) -> float:
        """
        Рассчитывает среднюю зарплату на основе salary_from и salary_to.

        :return: Средняя зарплата (или крайнее значение, если одно из полей отсутствует)
        :rtype: float
        """
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from:
            return self.salary_from
        elif self.salary_to:
            return self.salary_to
        else:
            return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект вакансии в словарь для сериализации.

        :return: Словарь с данными вакансии
        :rtype: Dict[str, Any]
        """
        return {
            "name": self.name,
            "url": self.url,
            "work_format": self.work_format,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to
        }

    @classmethod
    def created_vacancy(cls, vacancy_data: Dict[str, Any]) -> 'Vacancy':
        """
        Создаёт объект Vacancy из словаря с данными.

        :param vacancy_data: Словарь с данными вакансии (как из API)
        :type vacancy_data: Dict[str, Any]
        :return: Объект Vacancy
        :rtype: Vacancy
        """
        name = vacancy_data.get("name")
        # Исправлено: удалено лишнее кавычка в ключе
        url = vacancy_data.get("alternate_url")
        work_formats = []
        for work_format in vacancy_data.get("work_format", []):
            work_formats.append(work_format.get("name"))
        salary_info = vacancy_data.get("salary", {})
        if salary_info.get("currency") == "RUB":
            salary_from = salary_info.get("from")
            salary_to = salary_info.get("to")
        else:
            salary_from = None
            salary_to = None
        return cls(
            name=name,
            url=url,
            work_format=work_formats,
            salary_from=salary_from,
            salary_to=salary_to
        )

    @classmethod
    def cast_to_object_list(cls, vacancy_list: List[Dict[str, Any]]) -> List['Vacancy']:
        """
        Преобразует список словарей в список объектов Vacancy.

        :param vacancy_list: Список словарей с данными вакансий
        :type vacancy_list: List[Dict[str, Any]]
        :return: Список объектов Vacancy
        :rtype: List[Vacancy]
        """
        result = []
        for vac in vacancy_list:
            result.append(cls.created_vacancy(vac))
        return result

    @staticmethod
    def validate_vacancies(
            name: str,
            url: str,
            salary_from: Optional[int],
            salary_to: Optional[int]
    ) -> Dict[str, Any]:
        """
        Валидирует входные данные для создания вакансии.

        :param name: Название вакансии
        :type name: str
        :param url: URL вакансии
        :type url: str
        :param salary_from: Минимальная зарплата
        :type salary_from: Optional[int]
        :param salary_to: Максимальная зарплата
        :type salary_to: Optional[int]
        :return: Словарь с валидированными данными
        :rtype: Dict[str, Any]
        :raises ValueError: Если name или url пустые
        """
        if not name:
            raise ValueError("Название вакансии не может быть пустым")
        if not url:
            raise ValueError("URL вакансии не может быть пустым")

        # Явно обрабатываем None → 0 для обоих полей
        final_salary_from = salary_from if salary_from is not None else 0
        final_salary_to = salary_to if salary_to is not None else 0

        # Гарантируем возврат во всех случаях
        return {
            "name": name,
            "url": url,
            "salary_from": final_salary_from,
            "salary_to": final_salary_to
        }
