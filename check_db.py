import sqlite3

conn = sqlite3.connect("waste_accounting.db")
cursor = conn.cursor()

# Проверяем количество кодов
cursor.execute("SELECT COUNT(*) FROM fkko_codes")
count = cursor.fetchone()[0]
print(f"📊 Всего кодов ФККО в БД: {count}")

if count == 0:
    print("❌ БД пуста! Выполните инициализацию.")
    print("Запустите: python -c 'from database import init_database; init_database()'")
else:
    print("\n📋 Примеры кодов (первые 10):")
    cursor.execute("SELECT code_11, name, danger_class FROM fkko_codes LIMIT 10")
    for row in cursor.fetchall():
        print(f"   {row[0]} — {row[1]} (класс {row[2]})")

conn.close()