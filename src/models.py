from typing import Optional


class Vacancy:
    name: str
    url: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    work_format: str

    def __init__(
            self,
            name: str,
            url: str,
            work_format: str,
            salary_from: Optional[int] = None,
            salary_to: Optional[int]= None
    ):
        valid_date = self.validate_vacancies(name, url, salary_from, salary_to)
        self.name = valid_date.get("name")
        self.url = valid_date.get("url")
        self.work_format = work_format
        self.salary_from = valid_date.get("salary_from")
        self.salary_to = valid_date.get("salary_to")

    def __str__(self):
        if self.salary_from == 0 and self.salary_to == 0:
            salary_range = "не указано"
        elif self.salary_from == 0:
            salary_range = f"до {self.salary_to}"
        elif self.salary_to == 0:
            salary_range = f"от {self.salary_from}"
        else:
            salary_range = f"от {self.salary_from} до {self.salary_to}"
        result = (f"Вакансия {self.name} c {self.url}, "
                  f"зарплата {salary_range}, "
                  f"формат работы {self.work_format}")
        return result

    def __lt__(self, other: 'Vacancy') -> bool:
        return self.medium_salary() < other.medium_salary()

    def __le__(self, other):
        return self.medium_salary() <= other.medium_salary()

    def __gt__(self, other):
        return self.medium_salary() > other.medium_salary()

    def __ge__(self, other):
        return self.medium_salary() >= other.medium_salary()

    def medium_salary(self):
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from:
            return self.salary_from
        elif self.salary_to:
            return self.salary_to
        else:
            return 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "work_format": self.work_format,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to
        }

    @staticmethod
    def validate_vacancies(
            name: str,
            url: str,
            salary_from: Optional[int],
            salary_to: Optional[int]
    ):
        if not name:
            raise ValueError
        if not url:
            raise ValueError
        if not salary_from:
            salary_from = 0
        if not salary_to:
            salary_to = 0
        return {"name": name, "url": url, "salary_from": salary_from, "salary_to": salary_to}
