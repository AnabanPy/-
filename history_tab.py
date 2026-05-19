from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QHeaderView, QScrollArea)
from PyQt6.QtCore import Qt
from api_client import APIClient

STATUS_RUSSIAN = {
    "accepted": "Принят",
    "classified": "Классифицирован",
    "processing": "В обработке",
    "completed": "Завершен",
    "registered": "Зарегистрирован",
    "verified": "Проверен",
    "rejected": "Отклонен"
}


class HistoryTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.client = APIClient()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("История поступлений отходов")
        title.setObjectName("title")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Код", "Наименование", "Класс", "Объем (т)", "ФККО код", "Дата", "Статус", "Цех"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Увеличенный шрифт через стиль
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
            }
            QTableWidget::item {
                padding: 10px;
                font-size: 12pt;
            }
            QHeaderView::section {
                font-size: 13pt;
                padding: 12px;
            }
        """)

        scroll.setWidget(self.table)
        layout.addWidget(scroll)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)

    def load_data(self):
        try:
            batches = self.client.get_batches()
            self.table.setRowCount(len(batches))

            for i, batch in enumerate(batches):
                self.table.setItem(i, 0, QTableWidgetItem(str(batch.get('id', ''))))
                self.table.setItem(i, 1, QTableWidgetItem(batch.get('code', '')))
                self.table.setItem(i, 2, QTableWidgetItem(batch.get('name', '')[:60] if batch.get('name') else ''))

                hazard = batch.get('hazard_class', '')
                hazard_text = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(hazard, str(hazard))
                self.table.setItem(i, 3, QTableWidgetItem(hazard_text))

                vol = batch.get('volume_tons', 0)
                self.table.setItem(i, 4, QTableWidgetItem(f"{vol:.2f}" if vol else "0.00"))
                self.table.setItem(i, 5, QTableWidgetItem(batch.get('fkko_code', '—')[:25]))
                self.table.setItem(i, 6, QTableWidgetItem(
                    batch.get('received_at', '')[:10] if batch.get('received_at') else '—'))

                status_en = batch.get('status', '—')
                status_ru = STATUS_RUSSIAN.get(status_en, status_en)
                self.table.setItem(i, 7, QTableWidgetItem(status_ru))

                self.table.setItem(i, 8, QTableWidgetItem(batch.get('source_department', '—') or '—'))

            self.table.setColumnWidth(0, 70)
            self.table.setColumnWidth(1, 90)
            self.table.setColumnWidth(2, 280)
            self.table.setColumnWidth(3, 70)
            self.table.setColumnWidth(4, 90)
            self.table.setColumnWidth(5, 160)
            self.table.setColumnWidth(6, 110)
            self.table.setColumnWidth(7, 130)

            self.table.resizeRowsToContents()

        except Exception as e:
            print(f"Ошибка загрузки: {e}")