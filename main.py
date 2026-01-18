from src.api import HeadHunterAPI
from src.models import Vacancy
from src.storage import JsonSaver

def user_interaction():
    """
    Функция взаимодействия с пользователем через консоль.
    Позволяет:
    - искать вакансии на hh.ru;
    - показывать топ N по зарплате;
    - фильтровать по ключевому слову в названии.
    """
    hh_api = HeadHunterAPI(per_page=2)
    saver = JsonSaver("vacancies.json")

    print("Добро пожаловать в систему поиска вакансий!")
    while True:
        print("\nВыберите действие:")
        print("1. Поиск вакансий по запросу")
        print("2. Топ N вакансий по зарплате")
        print("3. Поиск по ключевому слову в названии")
        print("4. Выход")

        choice = input("Ваш выбор (1–4): ").strip()

        if choice == "1":
            query = input("Введите поисковый запрос: ").strip()
            if not query:
                print("Запрос не может быть пустым!")
                continue
            try:
                raw_vacancies = hh_api.get_vacancies(query)
                if not raw_vacancies:
                    print("Вакансий не найдено.")
                    continue
                # Преобразуем в объекты Vacancy
                vacancies = Vacancy.cast_to_object_list(raw_vacancies)
                # Сохраняем в файл
                if saver.add_date(vacancies):
                    print(f"Найдено {len(vacancies)} вакансий. Сохранено в файл.")
                else:
                    print("Ошибка при сохранении в файл.")
            except Exception as e:
                print(f"Ошибка при запросе к API: {e}")

        elif choice == "2":
            try:
                n = int(input("Сколько вакансий показать в топе? "))
                if n <= 0:
                    print("Число должно быть положительным.")
                    continue
                # Загружаем из файла
                all_vacancies = saver.read_data()
                if not all_vacancies:
                    print("Нет сохранённых вакансий.")
                    continue
                # Сортируем по средней зарплате (убывание)
                sorted_vacancies = sorted(all_vacancies, reverse=True)
                top_n = sorted_vacancies[:n]
                print(f"\nТоп {n} вакансий по зарплате:")
                for i, vac in enumerate(top_n, 1):
                    print(f"{i}. {vac}")
            except ValueError:
                print("Введите целое число.")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            keyword = input("Введите ключевое слово для поиска в названии: ").strip().lower()
            if not keyword:
                print("Слово не может быть пустым.")
                continue
            all_vacancies = saver.read_data()
            if not all_vacancies:
                print("Нет сохранённых вакансий.")
                continue
            # Фильтруем по подстроке в названии
            filtered = [v for v in all_vacancies if keyword in v.name.lower()]
            if not filtered:
                print("Вакансий не найдено.")
            else:
                print(f"\nНайжено {len(filtered)} вакансий:")
                for i, vac in enumerate(filtered, 1):
                    print(f"{i}. {vac}")

        elif choice == "4":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Введите 1, 2, 3 или 4.")


if __name__ == "__main__":
    user_interaction()
