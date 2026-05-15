import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from database import init_database
from auth import AuthManager
from main_window import MainWindow


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация — Модуль учета отходов")
        self.setFixedSize(350, 200)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()

        self.title_label = QLabel("Модуль учета и классификации отходов")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        layout.addWidget(self.login_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def authenticate(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        user = AuthManager.authenticate(login, password)
        if user:
            self.accept()
            self.main_window = MainWindow(user)
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Инициализация базы данных
    init_database()

    login_dialog = LoginDialog()
    login_dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()