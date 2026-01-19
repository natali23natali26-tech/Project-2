from typing import Optional, List, Dict, Any


class Vacancy:
    """
    Класс, представляющий вакансию.
    """
    # Экономия памяти
    __slots__ = (
        "name",
        "url",
        "work_format",
        "salary_from",
        "salary_to")

    def __init__(
            self,
            name: str,
            url: str,
            work_format: List[str],
            salary_from: Optional[int] = None,
            salary_to: Optional[int] = None
    ):
        # Вызов через класс
        valid_data = Vacancy._validate_vacancies(
            name,
            url,
            salary_from,
            salary_to
        )
        self.name = valid_data["name"]
        self.url = valid_data["url"]
        self.work_format = work_format if work_format else ["Не указано"]
        self.salary_from = valid_data["salary_from"]
        self.salary_to = valid_data["salary_to"]

    def __str__(self) -> str:
        salary_str = self._format_salary()
        work_format_str = ", ".join(self.work_format)
        return (
            f"Вакансия: {self.name}\n"
            f"Зарплата: {salary_str}\n"
            f"Формат: {work_format_str}\n"
            f"Ссылка: {self.url}\n"
        )

    def _format_salary(self) -> str:
        """Форматирует зарплату для отображения."""
        if self.salary_from == 0 and self.salary_to == 0:
            return "не указана"
        elif self.salary_to == 0:
            return f"от {self.salary_from} руб."
        elif self.salary_from == 0:
            return f"до {self.salary_to} руб."
        elif self.salary_from == self.salary_to:
            return f"{self.salary_from} руб."
        else:
            return f"от {self.salary_from} до {self.salary_to} руб."

    def __lt__(self, other: 'Vacancy') -> bool:
        return self.medium_salary() < other.medium_salary()

    def __le__(self, other: 'Vacancy') -> bool:
        return self.medium_salary() <= other.medium_salary()

    def __gt__(self, other: 'Vacancy') -> bool:
        return self.medium_salary() > other.medium_salary()

    def __ge__(self, other: 'Vacancy') -> bool:
        return self.medium_salary() >= other.medium_salary()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return False
        return self.medium_salary() == other.medium_salary()

    def medium_salary(self) -> float:
        """Рассчитывает среднюю зарплату."""
        if self.salary_from > 0 and self.salary_to > 0:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from > 0:
            return float(self.salary_from)
        elif self.salary_to > 0:
            return float(self.salary_to)
        else:
            return 0.0

    def has_salary(self) -> bool:
        """Проверяет, указана ли зарплата."""
        return self.salary_from > 0 or self.salary_to > 0

    @classmethod
    def created_vacancy(
            cls,
            vacancy_data: Dict[str, Any]
    ) -> Optional['Vacancy']:
        """Создаёт объект Vacancy из данных HH API."""
        try:
            name = (vacancy_data.get("name", "Без названия")
                    or "Без названия")
            url = (vacancy_data.get("alternate_url", "")
                   or vacancy_data.get("url", ""))

            work_formats = []
            # 1. schedule
            schedule = vacancy_data.get("schedule")
            if isinstance(schedule, dict):
                schedule_name = schedule.get("name", "")
                if schedule_name:
                    work_formats.append(schedule_name)
            # 2. employment
            employment = vacancy_data.get("employment")
            if isinstance(employment, dict):
                employment_name = employment.get("name", "")
                if employment_name:
                    work_formats.append(employment_name)
            # 3. work_format
            work_format_direct = vacancy_data.get("work_format")
            if work_format_direct:
                if isinstance(work_format_direct, str):
                    work_formats.append(work_format_direct)
                elif isinstance(work_format_direct, dict):
                    wf_name = work_format_direct.get("name", "")
                    if wf_name:
                        work_formats.append(wf_name)

            if not work_formats:
                work_formats = ["Не указано"]

            # Зарплата
            salary_info = vacancy_data.get("salary")
            salary_from = None
            salary_to = None
            if isinstance(salary_info, dict):
                currency = salary_info.get("currency", "")
                if currency.upper() in ["RUR", "RUB"]:
                    salary_from = salary_info.get("from")
                    salary_to = salary_info.get("to")

            return cls(
                name=name,
                url=url,
                work_format=work_formats,
                salary_from=salary_from,
                salary_to=salary_to
            )
        except Exception as e:
            print(f"Ошибка при создании вакансии: {e}")
            return None

    @classmethod
    def cast_to_object_list(
            cls,
            vacancy_list: List[Dict[str, Any]]
    ) -> List['Vacancy']:
        """Преобразует список словарей в список объектов Vacancy."""
        result = []
        if not vacancy_list or not isinstance(vacancy_list, list):
            return result

        print(f"\nНачинаю преобразование "
              f"{len(vacancy_list)} вакансий...")
        success_count = 0
        fail_count = 0

        for i, vac in enumerate(vacancy_list):
            try:
                if not isinstance(vac, dict):
                    fail_count += 1
                    continue
                vacancy_obj = cls.created_vacancy(vac)
                if vacancy_obj:
                    result.append(vacancy_obj)
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                if fail_count < 5:
                    print(f"Ошибка при создании вакансии #{i}: {e}")

        print(f"Преобразование завершено: "
              f"успешно {success_count}, "
              f"неудачно {fail_count}")
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект вакансии в словарь для сериализации."""
        return {
            "name": self.name,
            "url": self.url,
            "work_format": self.work_format,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to
        }

    @staticmethod
    def _validate_vacancies(
            name: str,
            url: str,
            salary_from: Optional[int],
            salary_to: Optional[int]
    ) -> Dict[str, Any]:
        """Приватная статическая валидация входных данных."""
        # Имя и URL
        if not name or not isinstance(name, str):
            name = "Без названия"
        if not url or not isinstance(url, str):
            url = ""

        # Зарплата
        if salary_from is None:
            salary_from = 0
        elif not isinstance(salary_from, (int, float)):
            salary_from = 0

        if salary_to is None:
            salary_to = 0
        elif not isinstance(salary_to, (int, float)):
            salary_to = 0

        return {
            "name": name.strip(),
            "url": url.strip(),
            "salary_from": int(salary_from),
            "salary_to": int(salary_to)
        }
