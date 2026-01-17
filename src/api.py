from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Any


class AbstractVacancyAPI(ABC):
    """
    Абстрактный класс для работы с API вакансий.

    Определяет контракт для классов‑реализаторов, обеспечивающих:
    - подключение к API;
    - получение списка вакансий по ключевому слову.
    """

    @abstractmethod
    def connect(self) -> Dict[str, Any]:
        """
        Устанавливает соединение с API и получает ответ.

        :return: JSON‑ответ от API в виде словаря
        :rtype: Dict[str, Any]
        :raises Exception: При ошибке HTTP‑запроса (статус ≠ 200)
        """
        pass

    @abstractmethod
    def get_vacancies(self, key_word: str) -> List[Dict[str, Any]]:
        """
        Получает список вакансий по заданному ключевому слову.

        :param key_word: Ключевое слово для поиска вакансий
        :type key_word: str
        :return: Список вакансий в формате, возвращаемом API
        :rtype: List[Dict[str, Any]]
        """
        pass


class HeadHunterAPI(AbstractVacancyAPI):
    """
    Реализация API для работы с HeadHunter (hh.ru).

    Позволяет:
    - подключаться к API hh.ru;
    - искать вакансии по ключевому слову;
    - ограничивать количество результатов на страницу.
    """

    def __init__(self, per_page: int = 100):
        """
        Инициализирует экземпляр API с заданными параметрами.

        :param per_page: Количество вакансий на одной странице (от 0 до 100)
        :type per_page: int
        :raises TypeError: Если per_page не является целым числом
        :raises ValueError: Если per_page вне диапазона [0, 100]
        """
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.per_page = self.__valid_per_page(per_page)
        self.__params = {"text": "", "page": 0, "per_page": self.per_page}
        self.__vacancies: List[Dict[str, Any]] = []

    def connect(self) -> Dict[str, Any]:
        """
        Публичный метод для подключения к API.

        Вызывает приватный метод __connect и возвращает его результат.

        :return: JSON‑ответ от API
        :rtype: Dict[str, Any]
        """
        return self.__connect()

    def __connect(self) -> Dict[str, Any]:
        """
        Приватный метод для выполнения HTTP‑запроса к API.

        :return: JSON‑ответ от API
        :rtype: Dict[str, Any]
        :raises Exception: Если статус ответа ≠ 200 (с описанием ошибки)
        """
        response = requests.get(self.__url, headers=self.__headers, params=self.__params)
        if response.status_code != 200:
            raise Exception(f"Ошибка API: {response.status_code} - {response.text}")
        else:
            return response.json()

    def get_vacancies(self, key_word: str) -> List[Dict[str, Any]]:
        """
        Получает список вакансий по ключевому слову с пагинацией.

        Выполняет запросы до 20 страниц или пока не закончатся результаты.

        :param key_word: Ключевое слово для поиска
        :type key_word: str
        :return: Список найденных вакансий
        :rtype: List[Dict[str, Any]]
        """
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
    def __valid_per_page(per_page: int) -> int:
        """
        Валидирует параметр per_page.

        Проверяет, что:
        - per_page является целым числом;
        - per_page находится в диапазоне [0, 100].

        :param per_page: Значение для проверки
        :type per_page: int
        :return: Валидированное значение per_page
        :rtype: int
        :raises TypeError: Если per_page не целое число
        :raises ValueError: Если per_page вне допустимого диапазона
        """
        if not isinstance(per_page, int):
            raise TypeError('Не является целым числом')
        if not 0 <= per_page <= 100:
            raise ValueError('не входит в диапазон от 0 до 100')
        return per_page


if __name__ == '__main__':
    hh_api = HeadHunterAPI(1)
    print(hh_api.get_vacancies('python'))
