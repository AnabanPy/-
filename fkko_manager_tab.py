import sqlite3

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QInputDialog, QMessageBox)
from database import get_db_connection
from models import User


class FkkoManagerTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Код ФККО", "Наименование", "Класс опасности", "Агрегатное состояние"])
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.clicked.connect(self.add_code)
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self.edit_code)
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_code)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, code_11, name, danger_class, aggregate_state FROM fkko_codes ORDER BY code_11")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        self.code_data = []
        for i, row in enumerate(rows):
            self.code_data.append(row[0])
            self.table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.table.setItem(i, 1, QTableWidgetItem(row[2]))
            class_text = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(row[3], str(row[3]))
            self.table.setItem(i, 2, QTableWidgetItem(class_text))
            self.table.setItem(i, 3, QTableWidgetItem(row[4] or ""))

        self.table.resizeColumnsToContents()

    def add_code(self):
        code, ok1 = QInputDialog.getText(self, "Добавление кода", "Введите 11-значный код ФККО:")
        if not ok1 or not code:
            return
        name, ok2 = QInputDialog.getText(self, "Добавление кода", "Введите наименование отхода:")
        if not ok2 or not name:
            return
        class_str, ok3 = QInputDialog.getText(self, "Добавление кода", "Введите класс опасности (1-5):")
        if not ok3 or not class_str.isdigit() or int(class_str) not in range(1, 6):
            QMessageBox.warning(self, "Ошибка", "Класс опасности должен быть от 1 до 5")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO fkko_codes (code_11, name, danger_class) VALUES (?, ?, ?)",
                           (code, name, int(class_str)))
            conn.commit()
            QMessageBox.information(self, "Успех", "Код добавлен")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такой код уже существует")
        conn.close()
        self.load_data()

    def edit_code(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите код для редактирования")
            return
        code_id = self.code_data[selected]
        new_name, ok = QInputDialog.getText(self, "Редактирование", "Введите новое наименование:")
        if ok and new_name:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE fkko_codes SET name = ? WHERE id = ?", (new_name, code_id))
            conn.commit()
            conn.close()
            self.load_data()

    def delete_code(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите код для удаления")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить этот код из справочника?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            code_id = self.code_data[selected]
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fkko_codes WHERE id = ?", (code_id,))
            conn.commit()
            conn.close()
            self.load_data()