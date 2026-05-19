from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QLabel,
                             QScrollArea, QHeaderView)
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


class ControlTab(QWidget):
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

        title = QLabel("Контроль классификации отходов")
        title.setObjectName("title")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Код", "Наименование", "Класс", "Статус"])
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

        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("✅ Подтвердить классификацию")
        self.confirm_btn.setMinimumHeight(40)
        self.confirm_btn.clicked.connect(self.confirm)
        self.reject_btn = QPushButton("❌ Отклонить")
        self.reject_btn.setMinimumHeight(40)
        self.reject_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.reject_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        try:
            batches = self.client.get_batches()
            # Партии со статусом 'accepted' (приняты, ожидают классификации)
            pending = [b for b in batches if b.get('status') == 'accepted']

            self.table.setRowCount(len(pending))
            self.batch_data = []

            for i, batch in enumerate(pending):
                self.batch_data.append(batch['id'])
                self.table.setItem(i, 0, QTableWidgetItem(str(batch['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(batch.get('code', '')))
                self.table.setItem(i, 2, QTableWidgetItem(batch.get('name', '')[:50] if batch.get('name') else ''))
                self.table.setItem(i, 3, QTableWidgetItem(str(batch.get('hazard_class', ''))))

                status_ru = STATUS_RUSSIAN.get(batch.get('status', ''), batch.get('status', ''))
                self.table.setItem(i, 4, QTableWidgetItem(status_ru))

            # Фиксируем ширину колонок
            self.table.setColumnWidth(0, 70)
            self.table.setColumnWidth(1, 90)
            self.table.setColumnWidth(2, 350)
            self.table.setColumnWidth(3, 80)

            self.table.resizeRowsToContents()
            print(f"Загружено партий на контроль: {len(pending)}")

        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def confirm(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите партию")
            return

        batch_id = self.batch_data[selected]
        try:
            result = self.client.classify_batch(batch_id, {
                "hazard_class": 3,
                "classification_note": "Подтверждено"
            })
            QMessageBox.information(self, "Успех", f"Партия #{batch_id} классифицирована")
            self.load_data()
            # Обновляем историю
            main_window = self.window()
            if hasattr(main_window, 'tabs'):
                for i in range(main_window.tabs.count()):
                    tab = main_window.tabs.widget(i)
                    if tab is not None and hasattr(tab, 'load_data'):
                        try:
                            tab.load_data()
                        except:
                            pass
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")

    def reject(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите партию")
            return

        reason, ok = QInputDialog.getText(self, "Причина отклонения", "Укажите причину:")
        if ok and reason:
            QMessageBox.information(self, "Успех", f"Партия отклонена.\nПричина: {reason}")
            self.load_data()