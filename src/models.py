from typing import Optional

class Vacancy:
    name: str
    url: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    work_format: list

    def __init__(
            self,
            name: str,
            url: str,
            work_format: list,
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
        result = (f"Вакансия {self.name} "
                  f"({self.url}), "
                  f"зарплата: {salary_range}, "
                  f"формат работы: {", ".join(self.work_format)}"
                  )
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

    @classmethod
    def created_vacancy(cls, vacancy_data):

        name = vacancy_data.get("name")
        url = vacancy_data.get("'alternate_url'")
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
            name = name,
            url = url,
            work_format = work_formats,
            salary_from = salary_from,
            salary_to = salary_to
        )

    @classmethod
    def cast_to_object_list(cls, vacancy_list):
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

if __name__ == '__main__':
    vacancy = Vacancy(
        name = "разработчик",
        url = "https://hh.ru/applicant/vacancy_response?vacancyId=129224803",
        work_format = ["Удалённо"],
        salary_from = 0,
        salary_to = 100000
    )
    print(vacancy)
    print(vacancy.to_dict())