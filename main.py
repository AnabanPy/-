import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont
from auth import LoginDialog
from api_client import APIClient


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Заставка при загрузке
    splash = QSplashScreen()
    splash.show()
    splash.showMessage("Загрузка модуля учета отходов...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    # Проверка соединения с сервером
    client = APIClient()
    try:
        health = client.get_health()
        print(f"Сервер: {health}")
    except Exception as e:
        splash.close()
        QMessageBox.critical(None, "Ошибка", f"Не удалось подключиться к серверу:\n{e}")
        return

    QTimer.singleShot(1500, splash.close)

    login_dialog = LoginDialog()
    login_dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()