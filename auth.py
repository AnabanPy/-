from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(420, 300)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowTitleHint)

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #212529;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(35, 35, 35, 35)

        # Заголовок
        title = QLabel("Модуль учета и классификации отходов")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #212529; margin-bottom: 10px;")
        layout.addWidget(title)

        # Логин
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.login_input.setMinimumHeight(40)
        layout.addWidget(self.login_input)

        # Пароль
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)

        # Кнопка входа
        self.login_btn = QPushButton("Войти")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)

        layout.addStretch()
        self.setLayout(layout)

    def authenticate(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if login == "operator1" and password == "12345":
            from main_window import MainWindow
            self.accept()
            self.main_window = MainWindow({"login": "operator1", "full_name": "Иванов И.И.", "role": "operator"})
            self.main_window.show()
        elif login == "chief1" and password == "12345":
            from main_window import MainWindow
            self.accept()
            self.main_window = MainWindow({"login": "chief1", "full_name": "Сидоров А.В.", "role": "chief"})
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")