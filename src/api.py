from abc import ABC, abstractmethod
import requests


class AbstractVacancyAPI(ABC):
    """Абстрактный класс для работы с API вакансий."""

    @abstractmethod
    def connect(self):
        """Устанавливает соединение с API."""
        pass

    @abstractmethod
    def get_vacancies(self, key_word):
        """Получает список вакансий по ключевому слову."""
        pass


class HeadHunterAPI(AbstractVacancyAPI):
    """Реализация API для работы с HeadHunter (hh.ru)."""

    def __init__(self, per_page=100):
        """
        Инициализирует экземпляр API.

        :param per_page: количество вакансий на странице (0–100)
        """
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.per_page = self.__valid_per_page(per_page)
        self.__params = {
            "text": "",
            "page": 0,
            "per_page": self.per_page}
        self.__vacancies = []

    def connect(self):
        """Подключается к API и возвращает данные."""
        try:
            response = requests.get(
                self.__url,
                headers=self.__headers,
                params=self.__params,
                timeout=10
            )
            # Вызовет исключение для 4xx/5xx статусов
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к API: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None

    def get_vacancies(self, key_word):
        """
        Получает список вакансий по ключевому слову.
        Гарантированно возвращает список (может быть пустым).
        """
        self.__params["text"] = key_word
        self.__params["page"] = 0
        self.__vacancies.clear()

        page = 0
        max_pages = 20  # Ограничение API HH

        while page < max_pages:
            self.__params["page"] = page
            data = self.connect()

            # Если данные не получены, прекращаем сбор
            if data is None:
                print(f"Не удалось получить данные со страницы {page}")
                break

            # Получаем вакансии из ответа
            vacancies = data.get("items", [])

            # Если вакансий нет, значит это последняя страница
            if not vacancies:
                break

            # Добавляем вакансии
            self.__vacancies.extend(vacancies)
            print(f"Страница {page + 1}: "
                  f"загружено {len(vacancies)} вакансий")

            # Проверяем, есть ли еще страницы
            pages = data.get("pages", 0)
            if page + 1 >= pages:
                break

            page += 1

        print(f"Всего загружено вакансий: "
              f"{len(self.__vacancies)}")
        # Гарантированно возвращаем список
        return self.__vacancies

    @staticmethod
    def __valid_per_page(per_page):
        """Валидирует параметр per_page."""
        if not isinstance(per_page, int):
            raise TypeError('per_page должен быть целым числом')
        if not 0 <= per_page <= 100:
            raise ValueError('per_page должен быть в диапазоне от 0 до 100')
        return per_page

# if __name__ == '__main__':
#     hh_api = HeadHunterAPI(10)
#     result = hh_api.get_vacancies('python')
#     print(f"Найдено вакансий: {len(result)}")
#     for vacancy in result[:5]:  # Выводим первые 5
#         print(f"- {vacancy.get('name', 'Без названия')}")
