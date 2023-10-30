import sqlite3

class DatabaseHelper:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    # Методы для работы с БД
    def close_connection(self):
        self.conn.close()

    def check_url_exist(self, url: str):
        return self.check_url_in_website_data(url) and self.check_url_in_queue(url)

    # Методы для работы с таблицей website_data
    def get_last_id(self):
        self.cursor.execute('SELECT MAX(ID) FROM website_data')
        last_id = self.cursor.fetchone()[0]
        if last_id == None:
            return 1
        return last_id
    
    def check_url_in_website_data(self, url: str):
        try:
            self.cursor.execute("SELECT * FROM website_data WHERE URL=?", (url,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
    
    def write_in_DB(self, url, screenshot_path, site_text):
        self.cursor.execute("INSERT INTO website_data (url, screenshot_path, site_text) VALUES (?, ?, ?)",
                            (url, screenshot_path, site_text))
        self.conn.commit()

    # Методы для работы с таблицей queue
    def add_to_queue(self, url: str):
        try:
            self.cursor.execute("INSERT INTO queue (URL) VALUES (?)", (url,))
            self.conn.commit()
            print(f'URL "{url}" добавлен в очередь')
        except sqlite3.Error as e:
            print("Ошибка при добавлении в очередь:", e)

    def check_url_in_queue(self, url: str):
        try:
            self.cursor.execute("SELECT * FROM queue WHERE URL=?", (url,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
    
    def remove_from_queue(self, url: str):
        try:
            self.cursor.execute("DELETE FROM queue WHERE url=?", (url,))
            self.conn.commit()
            print(f'URL "{url}" удален из очереди')
        except sqlite3.Error as e:
            print("Ошибка при удалении из очереди:", e)

    def get_first_from_queue(self):
        try:
            self.cursor.execute("SELECT url FROM queue ORDER BY RANDOM() LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                print("Очередь пуста")
                return None
        except sqlite3.Error as e:
            print("Ошибка при получении первой записи из очереди:", e)

    def get_url_with_min_domain_count(self):
        try:
            # Выбираем уникальные домены из таблицы "website_data" и подсчитываем количество записей для каждого домена
            self.cursor.execute('SELECT domain, COUNT(*) FROM website_data GROUP BY domain')
            domain_counts = self.cursor.fetchall()

            # Находим домен с наименьшим количеством записей
            min_domain = min(domain_counts, key=lambda x: x[1])

            # Выбираем URL из таблицы "queue" с наименьшим доменом
            self.cursor.execute('SELECT URL FROM queue WHERE domain_ID = (SELECT ID FROM domains WHERE domain = ?)', (min_domain[0],))
            url = self.cursor.fetchone()

            print(f"Выбранный URL с наименьшим доменом: {url[0]}")

            return url[0] if url else None
        except sqlite3.Error as e:
            print("Ошибка при получении записи из очереди с наименьшим количеством данных:", e)

    # Методы для работы с таблицей error_website
    def add_to_error(self, url: str):
        try:
            self.cursor.execute("INSERT INTO error_website (URL) VALUES (?)", (url,))
            self.conn.commit()
            print(f'URL "{url}" добавлен в список сайтов которые не получилось обработать')
        except sqlite3.Error as e:
            print("Ошибка при добавлении в список сайтов которые не получилось обработать:", e)

