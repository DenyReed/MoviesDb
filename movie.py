import pymysql
import configparser
import sqlite3
import os
from collections import Counter


config = configparser.ConfigParser()
config.sections()
config.read("configs.ini")

# Получение значений из секции [Database]
host = config.get('Database', 'Host')
user = config.get('Database', 'User')
password = config.get('Database', 'Password')
database = config.get('Database', 'Database')

# Подключение к базе данных MySQL
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cur = connection.cursor()

data_folder = 'data'
db_filename = 'movies.db'
db_path = os.path.join(data_folder, db_filename)

os.makedirs(data_folder, exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    count INTEGER NOT NULL
)
''')
conn.commit()

# Функция для добавления запроса в базу данных или увеличения счетчика
def log_query(query):
    cursor.execute('SELECT count FROM queries WHERE query = ?', (query,))
    result = cursor.fetchone()
    if result:
        new_count = result[0] + 1
        cursor.execute('UPDATE queries SET count = ? WHERE query = ?', (new_count, query))
    else:
        cursor.execute('INSERT INTO queries (query, count) VALUES (?, ?)', (query, 1))
    conn.commit()

def get_top_queries(top_n=10):
    cursor.execute('SELECT query, count FROM queries ORDER BY count DESC LIMIT ?', (top_n,))
    top_queries = cursor.fetchall()
    return top_queries

# Функция для поиска фильмов по названию
def search_movies_by_title(title):
    cur.execute('SELECT * FROM film WHERE title LIKE %s LIMIT 10', ('%' + title + '%',))
    results = cur.fetchall()
    return results

# Функция для поиска фильмов по актеру
def search_movies_by_actor(actor):
    cur.execute('''
            SELECT film.film_id, film.title, film.release_year
        FROM film
        JOIN film_actor ON film.film_id = film_actor.film_id
        JOIN actor ON film_actor.actor_id = actor.actor_id
        WHERE actor.first_name LIKE %s OR actor.last_name LIKE %s
        LIMIT 10
        ''', ('%' + actor + '%', '%' + actor + '%'))
    results = cur.fetchall()
    return results

# Функция для поиска фильмов по жанру
def search_movies_by_genre(genre):
    cur.execute('SELECT * FROM film WHERE special_features LIKE %s LIMIT 10', ('%' + genre + '%',))
    results = cur.fetchall()
    return results

# Функция для поиска фильмов по году
def search_movies_by_year(year):
    cur.execute('SELECT * FROM film WHERE release_year = %s LIMIT 10', (year,))
    results = cur.fetchall()
    return results


# Консольный интерфейс
def main():
    while True:
        print("\nВыберите действие:")
        print("1. Показать последние запросы")
        print("2. Поиск фильма по названию")
        print("3. Поиск фильма по актерам")
        print("4. Поиск по жанру")
        print("5. Поиск по году выпуска")
        print("6. Выйти")

        choice = input("Введите номер действия: ")

        if choice == '1':
            top_queries = get_top_queries()
            print("Топ 10 запросов:")
            for query, count in top_queries:
                print(f"{query}: {count}")

        elif choice == '2':
            title = input("Введите название фильма для поиска: ")
            log_query("Поиск фильма по названию: " + title)
            movies = search_movies_by_title(title)
            if movies:
                for movie in movies:
                    print(f"ID: {movie[0]}, Название: {movie[1]}, Актер: {movie[2]}, Год: {movie[3]}")
            else:
                print("Фильмы не найдены.")

        elif choice == '3':
            actor = input("Введите имя или фамилию актера для поиска: ")
            log_query("Поиск актера по имени или фамилии: " + actor)
            movies = search_movies_by_actor(actor)
            if movies:
                for movie in movies:
                    print(f"ID: {movie[0]}, Название: {movie[1]}, Год: {movie[2]}")
            else:
                print("Фильмы не найдены.")

        elif choice == '4':
            genre = input("Введите жанр для поиска: ")
            log_query("Поиск фильмов по жанру: " + genre)
            movies = search_movies_by_genre(genre)
            if movies:
                for movie in movies:
                    print(f"ID: {movie[0]}, Название: {movie[1]}, Жанр: {movie[2]}, Год: {movie[3]}, Актер: {movie[4]}")
            else:
                print("Фильмы не найдены.")

        elif choice == '5':
            year = int(input("Введите год для поиска: "))
            log_query("Поиск фильмов по году: " + str(year))
            movies = search_movies_by_year(year)
            if movies:
                for movie in movies:
                    print(f"ID: {movie[0]}, Название: {movie[1]}, Жанр: {movie[2]}, Год: {movie[3]}, Актер: {movie[4]}")
            else:
                print("Фильмы не найдены.")

        elif choice == '6':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == '__main__':
    main()