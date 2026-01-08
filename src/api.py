from abc import ABC, abstractmethod
import requests

class AbstractVacancyAPI(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_vacancies(self, key_word):
        pass

class HeadHunterAPI(AbstractVacancyAPI):

    def __init__(self, per_page = 100):
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.per_page = self.__valid_per_page(per_page)
        self.__params = {"text": "", "page": 0, "per_page": self.per_page}
        self.__vacancies = []

    def connect(self):
        return self.__connect()

    def __connect(self):
        response = requests.get(self.__url, headers = self.__headers, params = self.__params)
        if response.status_code != 200:
            raise Exception(f"Ошибка API: {response.status_code} - {response.text}")
        else:
            return response.json()

    def get_vacancies(self, key_word):
        self.__params["text"] = key_word
        self.__params["page"] = 0
        self.__vacancies.clear()
        while self.__params.get("page", 0) < 20:
            data = self.connect()
            vacancies = data.get("items", [])
            if not vacancies:
                break
            self.__vacancies.extend(vacancies)
            self.__params["page"] += 1
        return self.__vacancies

    @staticmethod
    def __valid_per_page(per_page):
        if not isinstance(per_page, int):
            raise TypeError('Не является целым числом')
        if not 0 <= per_page <= 100:
            raise ValueError('не входит в диапазон от 0 до 100')
        return per_page

if __name__ == '__main__':
    hh_api = HeadHunterAPI(1)
    print(hh_api.get_vacancies('python'))
