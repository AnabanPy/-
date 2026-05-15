from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QLabel, QDateEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import QDate
import pandas as pd
import sqlite3
from database import get_db_connection
from models import User


class ReportTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Цех:"))
        self.shop_combo = QComboBox()
        self.shop_combo.addItem("Все", None)
        self.load_shops()
        filter_layout.addWidget(self.shop_combo)

        filter_layout.addWidget(QLabel("Дата от:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate(2026, 1, 1))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("Дата до:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Кнопки отчетов
        btn_layout = QHBoxLayout()
        self.excel_btn = QPushButton("📊 Экспорт в Excel")
        self.excel_btn.clicked.connect(self.export_excel)
        self.summary_btn = QPushButton("📈 Сводка по классам опасности")
        self.summary_btn.clicked.connect(self.show_summary)
        btn_layout.addWidget(self.excel_btn)
        btn_layout.addWidget(self.summary_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        self.setLayout(layout)

    def load_shops(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM shops")
        for row in cursor.fetchall():
            self.shop_combo.addItem(row[1], row[0])
        conn.close()

    def export_excel(self):
        shop_id = self.shop_combo.currentData()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        conn = get_db_connection()
        query = '''
            SELECT b.registration_number, b.registration_date, s.name as shop, f.name as waste, 
                   f.code_11, f.danger_class, b.quantity, b.unit
            FROM batches b
            JOIN shops s ON b.shop_id = s.id
            JOIN fkko_codes f ON b.fkko_id = f.id
            WHERE b.registration_date BETWEEN ? AND ?
        '''
        params = [date_from, date_to]
        if shop_id:
            query += " AND b.shop_id = ?"
            params.append(shop_id)

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if df.empty:
            QMessageBox.warning(self, "Нет данных", "За выбранный период нет записей")
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "report.xlsx", "Excel files (*.xlsx)")
        if filepath:
            df.to_excel(filepath, index=False)
            QMessageBox.information(self, "Успех", f"Отчет сохранен: {filepath}")

    def show_summary(self):
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.danger_class, COUNT(*), SUM(b.quantity)
            FROM batches b
            JOIN fkko_codes f ON b.fkko_id = f.id
            WHERE b.registration_date BETWEEN ? AND ?
            GROUP BY f.danger_class
            ORDER BY f.danger_class
        ''', (date_from, date_to))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            QMessageBox.warning(self, "Нет данных", "За выбранный период нет записей")
            return

        msg = "📊 Сводка по классам опасности:\n\n"
        for row in rows:
            class_text = {1: "I (чрезвычайно опасный)", 2: "II (высокоопасный)",
                          3: "III (умеренно опасный)", 4: "IV (малоопасный)",
                          5: "V (практически неопасный)"}.get(row[0], str(row[0]))
            msg += f"Класс {class_text}: {row[1]} партий, {row[2]:.2f} тонн\n"

        QMessageBox.information(self, "Сводка", msg)