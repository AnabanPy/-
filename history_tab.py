from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHBoxLayout, QComboBox, QPushButton, QDateEdit, QLabel)
from PyQt6.QtCore import QDate
import sqlite3
from database import get_db_connection
from models import User


class HistoryTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Цех:"))
        self.shop_filter = QComboBox()
        self.shop_filter.addItem("Все", None)
        self.load_shops()
        self.shop_filter.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.shop_filter)

        filter_layout.addWidget(QLabel("Дата от:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate(2026, 1, 1))
        self.date_from.setCalendarPopup(True)
        self.date_from.dateChanged.connect(self.load_data)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("Дата до:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.dateChanged.connect(self.load_data)
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["№", "Дата", "Цех", "Отход", "Код ФККО", "Класс", "Кол-во", "Статус"])
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_shops(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM shops")
        for row in cursor.fetchall():
            self.shop_filter.addItem(row[1], row[0])
        conn.close()

    def load_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT b.registration_number, b.registration_date, s.name, f.name, f.code_11, f.danger_class, b.quantity, b.unit, b.status
            FROM batches b
            JOIN shops s ON b.shop_id = s.id
            JOIN fkko_codes f ON b.fkko_id = f.id
            WHERE 1=1
        '''
        params = []

        shop_id = self.shop_filter.currentData()
        if shop_id:
            query += " AND b.shop_id = ?"
            params.append(shop_id)

        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        query += " AND b.registration_date BETWEEN ? AND ?"
        params.extend([date_from, date_to])

        query += " ORDER BY b.registration_date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row[0]))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))
            self.table.setItem(i, 2, QTableWidgetItem(row[2]))
            self.table.setItem(i, 3, QTableWidgetItem(row[3]))
            self.table.setItem(i, 4, QTableWidgetItem(row[4]))
            class_text = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(row[5], str(row[5]))
            self.table.setItem(i, 5, QTableWidgetItem(class_text))
            self.table.setItem(i, 6, QTableWidgetItem(f"{row[6]} {row[7]}"))
            self.table.setItem(i, 7, QTableWidgetItem(row[8]))

        self.table.resizeColumnsToContents()