from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from register_tab import RegisterTab
from history_tab import HistoryTab
from control_tab import ControlTab
from fkko_tab import FkkoTab
from report_tab import ReportTab
import os


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Модуль учета отходов — {user['full_name']} ({user['role']})")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #ffffff; border-bottom: 2px solid #e0e4e8;")
        header_layout = QVBoxLayout(header)

        title = QLabel("Программный комплекс по учету и переработке промышленных отходов")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        role_text = "Оператор склада" if user['role'] == 'operator' else "Начальник склада"
        subtitle = QLabel(f"Модуль учета поступления и классификации отходов | {user['full_name']} | {role_text}")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # Вкладки
        self.tabs = QTabWidget()

        # Общие для всех вкладки
        self.tabs.addTab(HistoryTab(user), "📋 История поступлений")
        self.tabs.addTab(ReportTab(user), "📊 Отчеты и аналитика")

        # Для оператора
        if user['role'] == 'operator':
            self.tabs.addTab(RegisterTab(user), "➕ Регистрация партии")

        # Для начальника склада (chief)
        if user['role'] == 'chief':
            self.tabs.addTab(ControlTab(user), "✅ Контроль классификации")
            self.tabs.addTab(FkkoTab(user), "📚 Справочник ФККО")

        layout.addWidget(self.tabs)

        # Применяем стили
        style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())