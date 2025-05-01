# ============================================================================================================
# --- ИМПОРТЫ ---
# ============================================================================================================

from DB_utils.db_utils import (
    search_by_keyword, search_by_genre_with_year_filter, log_query,
    get_popular_queries, get_top_movies_for_query, get_connection,
    get_queries_by_genre, get_queries_by_year, search_by_keyword_with_year_filter
)
import re

# ============================================================================================================
# --- ОСНОВНОЕ МЕНЮ ПРОГРАММЫ ---
# ============================================================================================================

def main():

    genres = [
        "Action", "Animation", "Children", "Classics", "Comedy", "Documentary", "Drama",
        "Family", "Foreign", "Games", "Horror", "Music", "New", "Sci-Fi", "Sports", "Travel"
    ]

    while True:
        print("\n--- Movie Search ---")
        print("1. Поиск по ключевому слову")
        print("2. Поиск по жанру и году")
        print("3. Топ популярных поисковых запросов")
        print("0. Выход")
        choice = input("Выберите действие: ")

# ============================================================================================================
# --- 1. ПОИСК ПО КЛЮЧЕВОМУ СЛОВУ С ФИЛЬТРОМ ГОДА ---
# ============================================================================================================

        if choice == '1':
            keyword = input("Введите ключевое слово: ").strip()

            print("Введите фильтр по году (например: >2000, <=2015, =2005). Оставьте пустым для пропуска.")
            year_filter = input("Год или условие: ").strip()

            operator = None
            year = None

            if year_filter:
                for op in ['>=', '<=', '>', '<', '=']:
                    if year_filter.startswith(op):
                        operator = op
                        year = year_filter[len(op):].strip()
                        break
                else:
                    if year_filter.isdigit():               # если не найдено ни одного оператора, но строка — число
                        operator = '='
                        year = year_filter

            # Главное: вызываем функцию и сохраняем результат в films
            films = (
                search_by_keyword_with_year_filter(keyword, operator, int(year))
                if operator and year.isdigit()
                else search_by_keyword_with_year_filter(keyword)
            )

            if films:
                film_titles = [film['title'] for film in films]
                year_str = f"{operator}{year}" if operator else f"{year}" if year else ""
                if not year_str and films and 'release_year' in films[0]:
                    year_str = f"={films[0]['release_year']}"  # по умолчанию используем "="
                query_string = f"keyword:{keyword},year:{year_str}" if year_str else f"keyword:{keyword}"
                log_query(query_string, film_titles)

                print("\nНайденные фильмы:\n")
                print(f"{'Название':<40} | {'Год':^6} | Описание")
                print("-" * 100)

                start = 0
                while start < len(films):
                    for film in films[start:start + 10]:
                        title = film['title'][:40]
                        year = film['release_year']
                        description = film['description'][:100] + '...' if len(film['description']) > 100 else film[
                            'description']
                        print(f"{title:<40} | {year:^6} | {description}")
                    start += 10

                    if start < len(films):
                        print("\n1. Ещё 10 фильмов")
                        print("0. Вернуться в меню")
                        action = input("Выберите действие: ")
                        if action != '1':
                            break
                    else:
                        print("\nФильмы закончились. Нажмите Enter для возврата в меню.")
                        input()
                        break
            else:
                print("Фильмы не найдены.")


# ============================================================================================================
# --- 2. ПОИСК ПО ЖАНРУ С ФИЛЬТРОМ ГОДА ---
# ============================================================================================================

        elif choice == '2':
            print("Доступные жанры:")
            for i, g in enumerate(genres, 1):
                print(f"{i}. {g}")

            genre_input = input("Введите номер жанра или название (например, 1 или Action): ").strip()

            if genre_input.isdigit():
                genre_index = int(genre_input) - 1
                if 0 <= genre_index < len(genres):
                    genre = genres[genre_index]
                else:
                    print("Некорректный номер жанра!")
                    continue
            else:
                genre = genre_input.title()

            print("Введите фильтр по году (например: >2000, <=2015, =2005). Оставьте пустым для пропуска.")
            year_filter = input("Год или условие: ").strip()

            operator = None
            year = None

            if year_filter:
                for op in ['>=', '<=', '>', '<', '=']:
                    if year_filter.startswith(op):
                        operator = op
                        year = year_filter[len(op):].strip()
                        break
                else:
                    if year_filter.isdigit():
                        operator = '='
                        year = year_filter

            films = (
                search_by_genre_with_year_filter(genre, operator, int(year))
                if operator and year and year.isdigit()
                else search_by_genre_with_year_filter(genre)
            )

            if films:
                film_titles = [film['title'] for film in films]
                year_str = f"{operator}{year}" if operator else f"{year}" if year else ""
                if not year_str and films and 'release_year' in films[0]:
                    year_str = f"={films[0]['release_year']}"
                query_string = f"genre:{genre},year:{year_str}" if year_str else f"genre:{genre}"
                log_query(query_string, film_titles)

                print("\nНайденные фильмы:\n")
                print(f"{'Название':<40} | {'Год':^6} | Жанр")
                print("-" * 70)

                start = 0
                while start < len(films):
                    for film in films[start:start + 10]:
                        print(f"{film['title']:<40} | {film['release_year']:^6} | {film['category']}")
                    start += 10

                    if start < len(films):
                        print("\n1. Ещё 10 фильмов")
                        print("0. Вернуться в меню")
                        action = input("Выберите действие: ")
                        if action != '1':
                            break
                    else:
                        print("\nФильмы закончились. Нажмите Enter для возврата в меню.")
                        input()
                        break
            else:
                print("Фильмы не найдены.")

# ============================================================================================================
# --- 3. ПРОСМОТР ПОПУЛЯРНЫХ ЗАПРОСОВ ---
# ============================================================================================================

        elif choice == '3':
            while True:
                print("\n--- Поисковые запросы ---")
                print("1. Показать популярные запросы по жанру")
                print("2. Показать популярные запросы по году")
                print("3. Показать все поисковые запросы")
                print("4. Вернуться в главное меню")
                sub_choice = input("Выберите действие: ")

# ------------------------------------------------------------------------------------------------------------
# --- 3.1. ТОП ЗАПРОСОВ ПО ЖАНРУ ---
# ------------------------------------------------------------------------------------------------------------

                if sub_choice == '1':
                    print("\nДоступные жанры:")

                    for i, g in enumerate(genres, 1):
                        print(f"{i}. {g}")

                    genre_input = input("Введите номер жанра или название (например, 1 или Action): ").strip()

                    if genre_input.isdigit():
                        genre_index = int(genre_input) - 1

                        if 0 <= genre_index < len(genres):
                            genre = genres[genre_index]
                        else:
                            print("Некорректный номер жанра!")
                            continue

                    else:
                        genre = genre_input.title()
                    print(f"\nТоп запросов по жанру '{genre}':")

                    genre_queries = get_queries_by_genre(genre)

                    if genre_queries:
                        print(f"\n{'Запрос':<45} | {'Кол-во':^7} | Топ фильмов")
                        print("-" * 100)

                        for query, count in genre_queries:
                            top_movies = get_top_movies_for_query(query)
                            movies_str = ", ".join(top_movies) if top_movies else "Нет данных"
                            print(f"{query:<45} | {count:^7} | {movies_str}")
                    else:
                        print("Запросов не найдено.")

# ------------------------------------------------------------------------------------------------------------
# 3.2. ТОП ЗАПРОСОВ ПО ГОДУ
# ------------------------------------------------------------------------------------------------------------

                elif sub_choice == '2':
                    print("Введите фильтр по году (например: >2000, <=2015, =2005). Оставьте пустым для пропуска.")
                    year_filter = input("Год или условие: ").strip()
                    operator = None
                    year = None

                    if year_filter:
                        for op in ['>=', '<=', '>', '<', '=']:

                            if year_filter.startswith(op):
                                operator = op
                                year = year_filter[len(op):].strip()
                                break

                        else:
                            if year_filter.isdigit():
                                operator = '='
                                year = year_filter

                    if not year or not year.isdigit() or not (1990 <= int(year) <= 2025):
                        print("Некорректный ввод. Нужно указать год в диапазоне от 1990 до 2025.")
                        continue

                    target_year = int(year)
                    print(f"\nТоп запросов по условию 'год {operator} {target_year}':")

                    all_queries = get_popular_queries()  # теперь без лимита

                    matched_queries = []
                    for query, count in all_queries:
                        if "year:" in query:
                            try:
                                match = re.search(r"year:(>=|<=|>|<|=)?(\d{4})", query)
                                if match:
                                    query_operator = match.group(1) or '='
                                    query_year = int(match.group(2))
                                    op = operator if operator != '=' else '=='
                                    if eval(f"{query_year} {op} {target_year}"):
                                        matched_queries.append((query, count))
                            except (ValueError, IndexError):
                                continue

                    if matched_queries:
                        unique_queries = {}
                        for query, count in matched_queries:
                            if query not in unique_queries:
                                unique_queries[query] = count

                        print(f"\n{'Запрос':<45} | {'Кол-во':^7} | Топ фильмов")
                        print("-" * 100)
                        for query, count in unique_queries.items():
                            top_movies = get_top_movies_for_query(query)
                            movies_str = ", ".join(top_movies) if top_movies else "Нет данных"
                            print(f"{query:<45} | {count:^7} | {movies_str}")
                    else:
                        print("Запросов не найдено.")

# ------------------------------------------------------------------------------------------------------------
# --- 3.3. ОБЩИЙ ТОП ЗАПРОСОВ ---
# ------------------------------------------------------------------------------------------------------------

                elif sub_choice == '3':
                    queries = get_popular_queries(limit=10)
                    print("\nОбщие популярные запросы:\n")
                    print(f"{'Запрос':<45} | {'Кол-во':^7} | Топ фильмов")
                    print("-" * 100)

                    for query, count in queries:
                        top_movies = get_top_movies_for_query(query, top_n=5)
                        movies_str = ", ".join(top_movies) if top_movies else "Нет данных"
                        print(f"{query:<45} | {count:^7} | {movies_str}")

# ------------------------------------------------------------------------------------------------------------
# --- 3.4. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ ---
# ------------------------------------------------------------------------------------------------------------

                elif sub_choice == '4':
                    print("Возврат в главное меню.")
                    break

                else:
                    print("Некорректный выбор!")

# ============================================================================================================
# --- 0. ВЫХОД ИЗ ПРОГРАММЫ ---
# ============================================================================================================

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Некорректный выбор!")

# ============================================================================================================
# --- ЗАПУСК ОСНОВНОЙ ФУНКЦИИ ---
# ============================================================================================================

if __name__ == "__main__":
    main()
