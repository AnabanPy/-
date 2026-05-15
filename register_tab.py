from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QLineEdit, QPushButton, QListWidget, QCheckBox,
                             QMessageBox, QDateEdit)
from PyQt6.QtCore import QDate, QThread, pyqtSignal
import sqlite3
from database import get_db_connection
from models import User
from datetime import date


class SearchThread(QThread):
    results_signal = pyqtSignal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Используем LIKE с COLLATE NOCASE для регистронезависимого поиска
        cursor.execute(
            "SELECT id, code_11, name, danger_class FROM fkko_codes WHERE name LIKE ? LIMIT 30",
            (f"%{self.query}%",)
        )
        results = cursor.fetchall()
        conn.close()
        self.results_signal.emit(results)


class RegisterTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.selected_fkko_id = None
        self.results_data = []
        self.init_ui()
        self.check_fkko_count()

    def check_fkko_count(self):
        """Проверка количества кодов ФККО в БД (для отладки)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fkko_codes")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"[DEBUG] В БД {count} кодов ФККО")

        # Выведем первые 5 для проверки
        if count > 0:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT code_11, name, danger_class FROM fkko_codes LIMIT 5")
            for row in cursor.fetchall():
                print(f"[DEBUG] Пример: {row[0]} - {row[1]} (класс {row[2]})")
            conn.close()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("📅 Дата поступления:", self.date_edit)

        # Цех
        self.shop_combo = QComboBox()
        self.load_shops()
        form_layout.addRow("🏭 Цех-источник:", self.shop_combo)

        # Поиск отхода
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите наименование отхода (окалина, шлам, стружка)...")
        self.search_input.textChanged.connect(self.on_search)
        form_layout.addRow("🔍 Наименование отхода:", self.search_input)

        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(120)
        self.results_list.itemClicked.connect(self.on_code_selected)
        form_layout.addRow("📋 Найденные коды ФККО:", self.results_list)

        # Результаты
        self.code_display = QLineEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setPlaceholderText("Код появится после выбора из списка")
        form_layout.addRow("📌 Код ФККО:", self.code_display)

        self.class_display = QLineEdit()
        self.class_display.setReadOnly(True)
        self.class_display.setPlaceholderText("Класс появится после выбора из списка")
        form_layout.addRow("⚠️ Класс опасности:", self.class_display)

        # Количество
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("0.000")
        form_layout.addRow("⚖️ Количество:", self.quantity_input)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["тонн", "м³", "кг", "л"])
        form_layout.addRow("📏 Единица измерения:", self.unit_combo)

        # Чекбокс
        self.print_act_checkbox = QCheckBox("📄 Сформировать акт после сохранения")
        form_layout.addRow("", self.print_act_checkbox)

        layout.addLayout(form_layout)

        # Кнопки
        self.save_btn = QPushButton("💾 Сохранить партию")
        self.save_btn.clicked.connect(self.save_batch)
        layout.addWidget(self.save_btn)

        layout.addStretch()
        self.setLayout(layout)

    def load_shops(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM shops")
        for row in cursor.fetchall():
            self.shop_combo.addItem(row[1], row[0])
        conn.close()

    def on_search(self, text):
        print(f"[DEBUG] Поиск: '{text}'")
        if len(text) >= 2:
            self.search_thread = SearchThread(text)
            self.search_thread.results_signal.connect(self.update_results)
            self.search_thread.start()
        else:
            self.results_list.clear()
            self.results_data = []

    def update_results(self, results):
        print(f"[DEBUG] Найдено результатов: {len(results)}")
        self.results_list.clear()
        self.results_data = []

        for row in results:
            fkko_id = row[0]
            code_11 = row[1]
            name = row[2]
            danger_class = row[3]
            self.results_list.addItem(f"{code_11} — {name} (класс {danger_class})")
            self.results_data.append((fkko_id, code_11, name, danger_class))

        if len(results) == 0:
            self.results_list.addItem("❌ Ничего не найдено. Попробуйте: окалина, шлам, стружка, масло")

    def on_code_selected(self, item):
        idx = self.results_list.row(item)
        if idx < 0 or idx >= len(self.results_data):
            print(f"[DEBUG] Ошибка: индекс {idx} вне диапазона {len(self.results_data)}")
            return

        fkko_id, code_11, name, danger_class = self.results_data[idx]
        self.selected_fkko_id = fkko_id
        self.code_display.setText(code_11)

        class_text = {
            1: "I (чрезвычайно опасный)",
            2: "II (высокоопасный)",
            3: "III (умеренно опасный)",
            4: "IV (малоопасный)",
            5: "V (практически неопасный)"
        }.get(danger_class, str(danger_class))
        self.class_display.setText(class_text)

        print(f"[DEBUG] Выбран код: {code_11}, класс: {danger_class}")

    def generate_registration_number(self):
        today = date.today()
        prefix = f"П-{today.year}{today.month:02d}{today.day:02d}"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM batches WHERE registration_number LIKE ?", (f"{prefix}%",))
        count = cursor.fetchone()[0]
        conn.close()
        return f"{prefix}-{count + 1:03d}"

    def save_batch(self):
        if self.shop_combo.currentIndex() < 0 or self.shop_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Выберите цех-источник")
            return

        if not self.selected_fkko_id:
            QMessageBox.warning(self, "Ошибка", "Выберите код отхода из списка")
            return

        try:
            quantity = float(self.quantity_input.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите положительное количество")
            return

        reg_number = self.generate_registration_number()
        reg_date = self.date_edit.date().toString("yyyy-MM-dd")
        shop_id = self.shop_combo.currentData()
        unit = self.unit_combo.currentText()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO batches (registration_number, registration_date, shop_id, fkko_id, quantity, unit, operator_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reg_number, reg_date, shop_id, self.selected_fkko_id, quantity, unit, self.user.id, 'registered'))
        batch_id = cursor.lastrowid
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", f"Партия зарегистрирована!\nНомер: {reg_number}")

        if self.print_act_checkbox.isChecked():
            self.generate_act(batch_id, reg_number)

        self.clear_form()

    def generate_act(self, batch_id, reg_number):
        from docx import Document
        from datetime import date
        import os

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.registration_number, b.registration_date, b.quantity, b.unit,
                   s.name, f.name, f.code_11, f.danger_class, u.full_name
            FROM batches b
            JOIN shops s ON b.shop_id = s.id
            JOIN fkko_codes f ON b.fkko_id = f.id
            JOIN users u ON b.operator_id = u.id
            WHERE b.id = ?
        ''', (batch_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти данные партии")
            return

        os.makedirs("exports", exist_ok=True)
        doc = Document()
        doc.add_heading(f"АКТ ПРИЕМА-ПЕРЕДАЧИ №{reg_number}", 0)
        doc.add_paragraph(f"Дата: {date.today().strftime('%d.%m.%Y')}")
        doc.add_paragraph(f"Цех-источник: {row[4]}")
        doc.add_paragraph(f"Отход: {row[5]}")
        doc.add_paragraph(f"Код ФККО: {row[6]}")
        class_text = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(row[7], str(row[7]))
        doc.add_paragraph(f"Класс опасности: {class_text}")
        doc.add_paragraph(f"Количество: {row[2]} {row[3]}")
        doc.add_paragraph(f"Оператор: {row[8]}")

        filename = f"exports/act_{reg_number}.docx"
        doc.save(filename)
        QMessageBox.information(self, "Успех", f"Акт сформирован: {filename}")

    def clear_form(self):
        self.search_input.clear()
        self.results_list.clear()
        self.code_display.clear()
        self.class_display.clear()
        self.quantity_input.clear()
        self.selected_fkko_id = None
        self.results_data = []
        if self.shop_combo.count() > 0:
            self.shop_combo.setCurrentIndex(0)