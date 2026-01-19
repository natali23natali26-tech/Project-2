from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import List
from src.models import Vacancy


class AbstractJson(ABC):
    """
    Абстрактный класс для работы с хранилищем вакансий в формате JSON.
    Определяет контракт для классов-реализаторов, обеспечивающих:
    - чтение данных из JSON-файла;
    - добавление новых данных в хранилище;
    - удаление данных по идентификатору (URL).
    """

    @abstractmethod
    def read_data(self) -> List[Vacancy]:
        """
        Читает данные из JSON-файла и преобразует их в список объектов Vacancy.
        """
        pass

    @abstractmethod
    def add_data(self, data: List[Vacancy]) -> bool:
        """
        Добавляет список вакансий в хранилище.
        """
        pass

    @abstractmethod
    def delete_data(self, url: str) -> bool:
        """
        Удаляет вакансию из хранилища по указанному URL.
        """
        pass


class JsonSaver(AbstractJson):
    """
    Конкретная реализация хранилища вакансий в JSON-файле.
    Обеспечивает:
    - сохранение списка вакансий с проверкой на дубликаты;
    - чтение данных с обработкой возможных ошибок;
    - удаление отдельных записей по URL.
    """

    def __init__(self, filepath: str = "vacancies.json"):
        """
        Инициализирует экземпляр хранилища.
        """
        self.__filepath = Path(filepath)

    def read_data(self) -> List[Vacancy]:
        """
        Читает данные из JSON-файла и преобразует их в список объектов Vacancy.
        Обрабатывает следующие ошибки:
        - отсутствие файла;
        - некорректный JSON;
        - ошибки валидации данных при создании объектов Vacancy.
        """
        if not self.__filepath.exists():
            return []
        try:
            with open(self.__filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Преобразуем dict → Vacancy. Ожидаемые ошибки:
            # - KeyError (нет поля в JSON)
            # - TypeError (неверный тип данных)
            return [Vacancy(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            # JSON-файл пуст/нечитаем ИЛИ файл удалён
            return []
        except (KeyError, TypeError, ValueError) as e:
            # Ошибка валидации данных в Vacancy.__init__
            print(f"Ошибка при чтении данных из файла: {e}")
            return []

    def add_data(self, data: List[Vacancy]) -> bool:
        """
        Добавляет список вакансий в JSON-файл, избегая дубликатов.
        Дубликаты определяются по полю url. Данные сохраняются в формате,
        совместимом с методом to_dict() класса Vacancy.
        """
        try:
            existing = self.read_data()
            url_set = {v.url for v in existing}
            for vacancy in data:
                if vacancy.url not in url_set:
                    existing.append(vacancy)
                    url_set.add(vacancy.url)
            with open(self.__filepath, "w", encoding="utf-8") as f:
                json.dump([v.to_dict() for v in existing], f, ensure_ascii=False, indent=2)
            return True
        except (PermissionError, OSError) as e:
            print(f"Не удалось записать файл: {e}")
            return False
        except (TypeError, ValueError) as e:
            print(f"Ошибка кодирования данных в JSON: {e}")
            return False

    def delete_data(self, url: str) -> bool:
        """
        Удаляет запись о вакансии из JSON-файла по указанному URL.
        """
        try:
            data = self.read_data()
            filtered = [v for v in data if v.url != url]
            with open(self.__filepath, "w", encoding="utf-8") as f:
                json.dump([v.to_dict() for v in filtered], f, ensure_ascii=False, indent=2)
            return True
        except (PermissionError, OSError) as e:
            print(f"Не удалось удалить запись: {e}")
            return False
        except (TypeError, ValueError) as e:  # Вместо JSONEncodeError
            print(f"Ошибка кодирования данных при удалении: {e}")
            return False
