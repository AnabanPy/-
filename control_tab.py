from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QInputDialog, QMessageBox)
import sqlite3
from database import get_db_connection
from models import User


class ControlTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["№ партии", "Дата", "Цех", "Отход", "Код ФККО", "Статус"])
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("✅ Подтвердить классификацию")
        self.confirm_btn.clicked.connect(self.confirm_batch)
        self.reject_btn = QPushButton("❌ Отклонить с причиной")
        self.reject_btn.clicked.connect(self.reject_batch)
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.reject_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.id, b.registration_number, b.registration_date, s.name, f.name, f.code_11, b.status
            FROM batches b
            JOIN shops s ON b.shop_id = s.id
            JOIN fkko_codes f ON b.fkko_id = f.id
            WHERE b.status != 'verified'
            ORDER BY b.registration_date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        self.batch_data = []
        for i, row in enumerate(rows):
            self.batch_data.append(row[0])
            self.table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.table.setItem(i, 1, QTableWidgetItem(row[2]))
            self.table.setItem(i, 2, QTableWidgetItem(row[3]))
            self.table.setItem(i, 3, QTableWidgetItem(row[4]))
            self.table.setItem(i, 4, QTableWidgetItem(row[5]))
            self.table.setItem(i, 5, QTableWidgetItem(row[6]))

        self.table.resizeColumnsToContents()

    def confirm_batch(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите партию")
            return
        batch_id = self.batch_data[selected]

        conn = get_db_connection()
        cursor = conn.cursor()
        from datetime import date
        cursor.execute("UPDATE batches SET status = 'verified', verified_by = ?, verification_date = ? WHERE id = ?",
                       (self.user.id, date.today().isoformat(), batch_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Классификация подтверждена")
        self.load_data()

    def reject_batch(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите партию")
            return
        batch_id = self.batch_data[selected]

        reason, ok = QInputDialog.getText(self, "Причина отклонения", "Укажите причину отклонения:")
        if ok and reason:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE batches SET status = 'rejected' WHERE id = ?", (batch_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", f"Партия отклонена. Причина: {reason}")
            self.load_data()