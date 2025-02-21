import pymysql
import configparser

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

# Функция для записи запроса в DB
def log_query(query):
    cur.execute('SELECT * FROM denyreed_search_results WHERE search_text = %s LIMIT 1', (query,))
    results = cur.fetchall()

    if results:
        for result in results:
            newCount = result[1] + 1
            cur.execute('UPDATE denyreed_search_results SET count = %s WHERE search_text = %s', (newCount, query))
            connection.commit()
    else:
        cur.execute('INSERT INTO denyreed_search_results (search_text, count) VALUES (%s, %s)', (query, 1))
        connection.commit()
    return

# Функция для чтения последних запросов из DB
def read_last_queries():
    cur.execute('SELECT * FROM denyreed_search_results ORDER BY count DESC LIMIT 10')
    results = cur.fetchall()
    return results

# Функция для поиска фильмов по названию
def search_movies_by_title(title):
    cur.execute('SELECT * FROM film WHERE title LIKE %s LIMIT 10', ('%' + title + '%',))
    results = cur.fetchall()
    return results

# Функция для поиска фильмов по актеру
def search_movies_by_actor(actor):
    cur.execute('SELECT * FROM actor WHERE first_name or last_name LIKE %s LIMIT 10', ('%' + actor + '%',))
    results = cur.fetchall()
    return results

# Консольный интерфейс
def main():
    while True:
        print("\nВыберите действие:")
        print("1. Показать последние запросы")
        print("2. Поиск фильма по названию")
        print("3. Поиск фильма по актерам")
        print("4. Выйти")

        choice = input("Введите номер действия: ")

        if choice == '1':
            last_queries = read_last_queries()
            if last_queries:
                print("\nПоследние запросы:")
                for query in last_queries:
                    print(f"Поисковая строка: {query[0]}, Кол-во запросов: {query[1]}")
            else:
                print("Нет сохраненных запросов.")

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
                    print(f"ID: {movie[0]}, Название: {movie[1]}, Актер: {movie[2]}, Год: {movie[3]}")
            else:
                print("Фильмы не найдены.")

        elif choice == '4':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == '__main__':
    main()