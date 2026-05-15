import sqlite3
import hashlib
from datetime import date

DB_PATH = "waste_accounting.db"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Пользователи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT CHECK(role IN ('operator', 'ecologist', 'chief', 'admin'))
        )
    ''')

    # Цеха-источники
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Коды ФККО
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fkko_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_11 TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            danger_class INTEGER CHECK(danger_class BETWEEN 1 AND 5),
            aggregate_state TEXT,
            origin TEXT
        )
    ''')

    # Партии отходов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_number TEXT UNIQUE NOT NULL,
            registration_date TEXT NOT NULL,
            shop_id INTEGER REFERENCES shops(id),
            fkko_id INTEGER REFERENCES fkko_codes(id),
            quantity REAL NOT NULL,
            unit TEXT DEFAULT 'тонн',
            operator_id INTEGER REFERENCES users(id),
            status TEXT DEFAULT 'registered',
            verified_by INTEGER REFERENCES users(id),
            verification_date TEXT
        )
    ''')

    # Документы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER REFERENCES batches(id),
            document_type TEXT CHECK(document_type IN ('act', 'passport')),
            file_path TEXT,
            created_at TEXT
        )
    ''')

    # Добавление начальных данных
    cursor.execute("SELECT COUNT(*) FROM shops")
    if cursor.fetchone()[0] == 0:
        shops = [
            ("Цех №1 (прокатный)", "Прокатный стан, образование окалины"),
            ("Цех №2 (механический)", "Механическая обработка металлов"),
            ("Цех №3 (гальванический)", "Гальваническое производство, шламы")
        ]
        cursor.executemany("INSERT INTO shops (name, description) VALUES (?, ?)", shops)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ("operator1", hash_password("12345"), "Иванов И.И.", "operator"),
            ("ecologist1", hash_password("12345"), "Петрова Е.Н.", "ecologist"),
            ("chief1", hash_password("12345"), "Сидоров А.В.", "chief"),
            ("admin", hash_password("admin123"), "Администратор", "admin")
        ]
        cursor.executemany("INSERT INTO users (login, password_hash, full_name, role) VALUES (?, ?, ?, ?)", users)

    cursor.execute("SELECT COUNT(*) FROM fkko_codes")
    if cursor.fetchone()[0] == 0:
        codes = [
            ("36121101714", "Окалина стальная", 4, "твердое", "прокатное производство"),
            ("36121102714", "Окалина чугунная", 4, "твердое", "прокатное производство"),
            ("46110101213", "Шлам масляный", 3, "жидкое", "механическая обработка"),
            ("47120101512", "Шлам гальванический (содержит хром)", 2, "жидкое", "гальваническое производство"),
            ("47120101513", "Шлам гальванический (содержит никель)", 2, "жидкое", "гальваническое производство"),
            ("35121101714", "Стружка стальная", 4, "твердое", "механическая обработка"),
            ("35121102714", "Стружка чугунная", 4, "твердое", "механическая обработка"),
            ("91100001115", "Отходы бумаги и картона", 5, "твердое", "административно-хозяйственные"),
            ("92110001115", "Отходы пластмасс", 5, "твердое", "упаковка"),
            ("47110101513", "Отработанные масла", 3, "жидкое", "обслуживание оборудования")
        ]
        cursor.executemany(
            "INSERT INTO fkko_codes (code_11, name, danger_class, aggregate_state, origin) VALUES (?, ?, ?, ?, ?)",
            codes)

    conn.commit()
    conn.close()


def get_db_connection():
    return sqlite3.connect(DB_PATH)