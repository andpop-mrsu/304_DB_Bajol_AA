import csv
import re
import os

print("Начало генерации SQL-скрипта")

DATASET_DIR = "../dataset"
OUTPUT_FILE = "db_init.sql"

# Открываем файл для записи SQL-команд
with open(OUTPUT_FILE, "w", encoding="utf-8") as sql_file:
    # 1. Создаем команды удаления старых таблиц (если они есть)
    sql_file.write("DROP TABLE IF EXISTS ratings;\n")
    sql_file.write("DROP TABLE IF EXISTS tags;\n")
    sql_file.write("DROP TABLE IF EXISTS movies;\n")
    sql_file.write("DROP TABLE IF EXISTS users;\n\n")

    # 2. Создаем таблицы
    sql_file.write("""
    CREATE TABLE movies (
        id INTEGER PRIMARY KEY,
        title TEXT,
        year INTEGER,
        genres TEXT
    );

    CREATE TABLE ratings (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        movie_id INTEGER,
        rating REAL,
        timestamp INTEGER
    );

    CREATE TABLE tags (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        movie_id INTEGER,
        tag TEXT,
        timestamp INTEGER
    );

    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        gender TEXT,
        register_date TEXT,
        occupation TEXT
    );\n\n
    """)

    # Начинаем транзакцию для быстрой загрузки
    sql_file.write("BEGIN TRANSACTION;\n\n")

    # --- Обработка MOVIES ---
    print("Обработка movies.csv")
    with open(os.path.join(DATASET_DIR, "movies.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = row['movieId']
            title_raw = row['title']
            genres = row['genres'].replace("'", "''")  # Экранируем кавычки для SQL

            # Извлекаем год из названия (например, "Toy Story (1995)")
            match = re.search(r'\((\d{4})\)$', title_raw)
            if match:
                year = match.group(1)
                title = title_raw[:match.start()].strip()
            else:
                year = "NULL"
                title = title_raw

            title = title.replace("'", "''")  # Экранируем кавычки

            sql_file.write(
                f"INSERT INTO movies (id, title, year, genres) VALUES ({movie_id}, '{title}', {year}, '{genres}');\n")

    # --- Обработка RATINGS ---
    print("Обработка ratings.csv")
    with open(os.path.join(DATASET_DIR, "ratings.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):  # Генерируем id с 1
            sql_file.write(
                f"INSERT INTO ratings (id, user_id, movie_id, rating, timestamp) VALUES ({i}, {row['userId']}, {row['movieId']}, {row['rating']}, {row['timestamp']});\n")

    # --- Обработка TAGS ---
    print("Обработка tags.csv")
    with open(os.path.join(DATASET_DIR, "tags.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):  # Генерируем id с 1
            tag = row['tag'].replace("'", "''")
            sql_file.write(
                f"INSERT INTO tags (id, user_id, movie_id, tag, timestamp) VALUES ({i}, {row['userId']}, {row['movieId']}, '{tag}', {row['timestamp']});\n")

    # --- Обработка USERS ---
    print("Обработка users.txt")
    with open(os.path.join(DATASET_DIR, "users.txt"), "r", encoding="utf-8") as f:
        for row in f:
            parts = row.strip().split('|')  # Разделитель - вертикальная черта
            if len(parts) == 6:
                uid, name, email, gender, reg_date, occupation = parts
                name = name.replace("'", "''")
                email = email.replace("'", "''")
                sql_file.write(
                    f"INSERT INTO users (id, name, email, gender, register_date, occupation) VALUES ({uid}, '{name}', '{email}', '{gender}', '{reg_date}', '{occupation}');\n")

    # Завершаем транзакцию
    sql_file.write("\nCOMMIT;\n")

print("Готово! Файл db_init.sql успешно создан.")