from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QScrollArea, QHeaderView)
from api_client import APIClient


class FkkoTab(QWidget):
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

        title = QLabel("Справочник видов отходов (ФККО)")
        title.setObjectName("title")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Код", "Наименование", "Код ФККО", "Класс"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Увеличенный шрифт
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                font-size: 13pt;
                padding: 12px;
            }
        """)

        scroll.setWidget(self.table)
        layout.addWidget(scroll)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)

    def load_data(self):
        try:
            waste_types = self.client.get_waste_types()
            self.table.setRowCount(len(waste_types))

            for i, wt in enumerate(waste_types):
                self.table.setItem(i, 0, QTableWidgetItem(str(wt.get('id', ''))))
                self.table.setItem(i, 1, QTableWidgetItem(wt.get('code', '')))
                self.table.setItem(i, 2, QTableWidgetItem(wt.get('name', '')))
                self.table.setItem(i, 3, QTableWidgetItem(wt.get('fkko_code', '')))

                hazard = wt.get('hazard_class', '')
                hazard_text = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}.get(hazard, str(hazard))
                self.table.setItem(i, 4, QTableWidgetItem(hazard_text))

            # Фиксируем ширину колонок
            self.table.setColumnWidth(0, 60)
            self.table.setColumnWidth(1, 100)
            self.table.setColumnWidth(2, 280)
            self.table.setColumnWidth(3, 150)

            self.table.resizeRowsToContents()
            print(f"Загружено видов отходов: {len(waste_types)}")

        except Exception as e:
            print(f"Ошибка: {e}")