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
        self.__params = {"text": "", "page": 0, "per_page": self.per_page}
        self.__vacancies = []

    def connect(self):
        try:
            result = self.__connect()
            print(f"Результат connect(): {result}")  # Отладка
            return result
        except Exception as e:
            print(f"Ошибка в connect(): {e}")
            return None

    def __connect(self):
        try:
            response = requests.get(
                self.__url,
                headers=self.__headers,
                params=self.__params,
                timeout=10
            )

            # Логируем статус и URL для отладки
            print(f"[Page {self.__params['page']}] Status: {response.status_code}, URL: {response.url}")

            if response.status_code != 200:
                print(f"[Page {self.__params['page']}] API Error: {response.status_code} — {response.text}")
                return None

            # Пытаемся парсить JSON
            try:
                json_data = response.json()
                return json_data
            except ValueError as e:
                print(f"[Page {self.__params['page']}] JSON Parse Error: {e}")
                print(f"[Page {self.__params['page']}] Raw Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"[Page {self.__params['page']}] Request Failed: {e}")
            return None
        except Exception as e:
            print(f"[Page {self.__params['page']}] Unexpected Error: {e}")
            return None

    def get_vacancies(self, key_word):
        self.__params["text"] = key_word
        self.__params["page"] = 0
        self.__vacancies.clear()

        while self.__params.get("page", 0) < 10:  # Лимит 20 страниц
            data = self.connect()

            # 1. Если connect() вернул None — прерываем
            if data is None:
                print(f"[Page {self.__params['page']}] connect() returned None. Stopping.")
                break

            # 2. Проверяем, что data — словарь
            if not isinstance(data, dict):
                print(f"[Page {self.__params['page']}] Response is not dict: {type(data)}")
                break

            # 3. Проверяем наличие 'items' и что это список
            if 'items' not in data:
                print(f"[Page {self.__params['page']}] 'items' key missing in response.")
                break

            if not isinstance(data['items'], list):
                print(f"[Page {self.__params['page']}] 'items' is not a list: {type(data['items'])}")
                break

            vacancies = data['items']

            # 4. Если вакансий нет — это конец данных
            if not vacancies:
                print(f"[Page {self.__params['page']}] No vacancies found. Stopping.")
                break

            self.__vacancies.extend(vacancies)
            print(f"[Page {self.__params['page']}] Loaded {len(vacancies)} vacancies.")

            self.__params["page"] += 1

            # 5. Пауза между запросами (чтобы не забанили)
            import time
            time.sleep(0.5)

        return self.__vacancies

    @staticmethod
    def __valid_per_page(per_page):
        """Валидирует параметр per_page."""
        if not isinstance(per_page, int):
            raise TypeError('per_page должен быть целым числом')
        if not 0 <= per_page <= 2:
            raise ValueError('per_page должен быть в диапазоне от 0 до 100')
        return per_page

# if __name__ == '__main__':
#     hh_api = HeadHunterAPI(10)
#     result = hh_api.get_vacancies('python')
#     print(f"Найдено вакансий: {len(result)}")
#     for vacancy in result[:5]:  # Выводим первые 5
#         print(f"- {vacancy.get('name', 'Без названия')}")
