import mysql.connector
import re
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================================================================
# 1. Конфигурация подключения к базам данных
# ============================================================================================================

dbconfig_sakila = {
    'host': os.getenv("SAKILA_HOST"),
    'user': os.getenv("SAKILA_USER"),
    'password': os.getenv("SAKILA_PASSWORD"),
    'database': os.getenv("SAKILA_DATABASE")
}

dbconfig_logs = {
    'host': os.getenv("LOGS_HOST"),
    'user': os.getenv("LOGS_USER"),
    'password': os.getenv("LOGS_PASSWORD"),
    'database': os.getenv("LOGS_DATABASE")
}

# Универсальная функция подключения к нужной базе
def get_connection(dbconfig):
    return mysql.connector.connect(**dbconfig)


# ============================================================================================================
# 2. Поиск фильмов
# ============================================================================================================

# Ищет фильмы по ключевому слову (в названии или описании)
def search_by_keyword(keyword):
    conn = get_connection(dbconfig_sakila)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT title, description, release_year
        FROM film
        WHERE LOWER(title) LIKE %s OR LOWER(description) LIKE %s
        LIMIT 20
    """, (f'%{keyword.lower()}%', f'%{keyword.lower()}%'))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Ищет фильмы по ключевому слову и фильтру по году
def search_by_keyword_with_year_filter(keyword, operator=None, year=None):
    conn = get_connection(dbconfig_sakila)
    cursor = conn.cursor(dictionary=True)

    if operator and year:
        query = f"""
            SELECT title, description, release_year
            FROM film
            WHERE (LOWER(title) LIKE %s OR LOWER(description) LIKE %s)
            AND release_year {operator} %s
            LIMIT 100
        """
        params = (f'%{keyword.lower()}%', f'%{keyword.lower()}%', year)
    else:
        query = """
            SELECT title, description, release_year
            FROM film
            WHERE LOWER(title) LIKE %s OR LOWER(description) LIKE %s
            LIMIT 100
        """
        params = (f'%{keyword.lower()}%', f'%{keyword.lower()}%')

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Ищет фильмы по жанру и фильтру по году
def search_by_genre_with_year_filter(genre, operator=None, year=None):
    conn = get_connection(dbconfig_sakila)
    cursor = conn.cursor(dictionary=True)

    if operator and year:
        query = f"""
            SELECT f.title, f.release_year, c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s AND f.release_year {operator} %s
            LIMIT 100
        """
        params = (genre, year)
    else:
        query = """
            SELECT f.title, f.release_year, c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s
            LIMIT 100
        """
        params = (genre,)

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# ============================================================================================================
# 3. Логирование поисковых запросов
# ============================================================================================================

# Извлекает жанр и год из строки запроса, если есть
def extract_genre_year(query_str):
    genre = None
    year = None
    genre_match = re.search(r"genre:([^,]+)", query_str)
    year_match = re.search(r"year:(\d{4})", query_str)
    if genre_match:
        genre = genre_match.group(1)
    if year_match:
        year = int(year_match.group(1))
    return genre, year

# Сохраняет запрос в базу логов (с фильмами, если они есть)
def log_query(query, film_titles=None):
    conn = get_connection(dbconfig_logs)
    cursor = conn.cursor()

    genre, year = extract_genre_year(query)

    if film_titles:
        films_str = "; ".join(film_titles)
        cursor.execute(
            "INSERT INTO query_logs (query, film_title, genre, year) VALUES (%s, %s, %s, %s)",
            (query, films_str, genre, year)
        )
    else:
        cursor.execute(
            "INSERT INTO query_logs (query, genre, year) VALUES (%s, %s, %s)",
            (query, genre, year)
        )

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================================================================
# 4. Получение статистики
# ============================================================================================================

# Возвращает список самых частых запросов (топ-10)
def get_popular_queries(limit=None):
    conn = get_connection(dbconfig_logs)
    cursor = conn.cursor()
    if limit:
        cursor.execute(f"""
            SELECT query, COUNT(*) as count
            FROM query_logs
            GROUP BY query
            ORDER BY count DESC
            LIMIT {limit}
        """)
    else:
        cursor.execute("""
            SELECT query, COUNT(*) as count
            FROM query_logs
            GROUP BY query
            ORDER BY count DESC
        """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Возвращает топ запросов по жанру (если не было найдено фильмов)
def get_queries_by_genre(genre):
    conn = get_connection(dbconfig_logs)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT query, COUNT(*) as count
        FROM query_logs
        WHERE genre = %s
        GROUP BY query
        ORDER BY count DESC
        LIMIT 10
    """, (genre,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Возвращает топ запросов по году (если не было найдено фильмов)
def get_queries_by_year(year):
    conn = get_connection(dbconfig_logs)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT query, COUNT(*) as count
        FROM query_logs
        WHERE year = %s AND film_title IS NULL
        GROUP BY query
        ORDER BY count DESC
        LIMIT 10
    """, (year,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# ============================================================================================================
# 5. Топ фильмов по запросу
# ============================================================================================================

# Возвращает популярные фильмы по запросу (если он уже встречался)
def get_top_movies_for_query(query, top_n=5):
    conn = get_connection(dbconfig_logs)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT film_title
        FROM query_logs
        WHERE query = %s AND film_title IS NOT NULL
    """, (query,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    film_counter = {}
    for row in rows:
        titles = row[0].split(";")
        for title in titles:
            title = title.strip()
            if title:
                film_counter[title] = film_counter.get(title, 0) + 1

    sorted_films = sorted(film_counter.items(), key=lambda x: x[1], reverse=True)
    return [title for title, _ in sorted_films[:top_n]]