from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import List
from src.models import Vacancy


class AbstractJson(ABC):
    @abstractmethod
    def read_data(self) -> List[Vacancy]:
        pass

    @abstractmethod
    def add_date(self, data: List[Vacancy]) -> bool:
        pass

    @abstractmethod
    def delete_data(self, url: str) -> bool:
        pass



class JsonSaver(AbstractJson):
    def __init__(self, filepath: str = "vacancies.json"):
        self.__filepath = Path(filepath)

    def read_data(self) -> List[Vacancy]:
        """Читает данные из JSON-файла. Возвращает пустой список при ошибках."""
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

    def add_date(self, data: List[Vacancy]) -> bool:
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
        except (TypeError, ValueError) as e:  # Вместо JSONEncodeError
            print(f"Ошибка кодирования данных в JSON: {e}")
            return False

    def delete_data(self, url: str) -> bool:
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
