from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt
from register_tab import RegisterTab
from history_tab import HistoryTab
from control_tab import ControlTab
from fkko_manager_tab import FkkoManagerTab
from report_tab import ReportTab


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Модуль учета отходов — {user.full_name} ({user.role})")
        self.setGeometry(100, 100, 1300, 750)

        self.tabs = QTabWidget()

        # Общие вкладки
        self.tabs.addTab(HistoryTab(user), "📋 История поступлений")
        self.tabs.addTab(ReportTab(user), "📊 Отчеты и аналитика")

        # Вкладки по ролям
        if user.role == 'operator':
            self.tabs.addTab(RegisterTab(user), "➕ Регистрация партии")

        if user.role in ('ecologist', 'chief', 'admin'):
            self.tabs.addTab(ControlTab(user), "✅ Контроль классификации")

        if user.role in ('ecologist', 'admin'):
            self.tabs.addTab(FkkoManagerTab(user), "📚 Справочник ФККО")

        self.setCentralWidget(self.tabs)

        # Применяем стили
        with open("styles.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())