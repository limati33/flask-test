import sqlite3

DATABASE = 'instance/reviews.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        unique_id TEXT NOT NULL,
                        nickname TEXT NOT NULL DEFAULT 'Аноним');
                    ''')

    # Изменяем таблицу объявлений, чтобы включить title
    conn.execute('''CREATE TABLE IF NOT EXISTS announcements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,  -- Добавляем поле для названия
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        image_path TEXT
                    );''')
    conn.close()
    print("База данных инициализирована.")

if __name__ == "__main__":
    init_db()
