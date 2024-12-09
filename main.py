import sys

import main_window
import create_client_window
import login_window
import loyal_system_settings
import report_page
import set_equipment_window
import set_gamesession_window
import set_hall_window

from PyQt6.QtWidgets import QApplication, QMainWindow, QButtonGroup, QMessageBox, QTableWidgetItem, QFileDialog

class Comp_club_main(QMainWindow, main_window.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.create_session_button.clicked.connect(self.open_gamesession_settings)
        self.loyal_system_button.clicked.connect(self.open_loyal_system_settings)
        self.create_client_button.clicked.connect(self.open_client_settings)
        self.create_equipment_button.clicked.connect(self.open_equipment_settings)

        self.tabWidget.resizeEvent = self.check_resize

        self.list_of_reports.addItem('test1')
        self.list_of_reports.addItem('test2')
        self.list_of_reports.addItem('test3')


    def check_resize(self, event):
        tab_width = self.tabWidget.width() // 4
        style = f"""
        QTabBar::tab {{
            width: {tab_width}px;
            height: 90px;
            background-color: rgb(41, 85, 180);
            color: white;
            border: 0px solid transparent;
            margin: 0px;
            padding: 0px;
        }}
        QTabBar::tab:selected {{
            background-color: #131936;
            color: white;
            border: none;
        }}
        """
        self.tabWidget.setStyleSheet(style)

    def open_gamesession_settings(self):
        self.setEnabled(False)
        self.window = Gamesessions(self)
        self.window.show()

    def open_loyal_system_settings(self):
        self.setEnabled(False)
        self.window = Loyal_system(self)
        self.window.show()

    def open_client_settings(self):
        self.setEnabled(False)
        self.window = Clients(self)
        self.window.show()

    def open_equipment_settings(self):
        self.setEnabled(False)
        self.window = Equipment(self)
        self.window.show()


class Clients(QMainWindow, create_client_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Login(QMainWindow, login_window.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.login = self.edit_login.text()
        self.password = self.edit_password.text()
        self.edit_login.textChanged.connect(self.change_login)
        self.edit_password.textChanged.connect(self.change_password)
        self.login_button.clicked.connect(self.start_app)


    def start_app(self):
        if self.password == '' and self.login == '':
            self.window = Comp_club_main()
            self.window.show()
            self.close()


    def change_login(self, text):
        self.login = text

    def change_password(self, text):
        self.password = text


class Loyal_system(QMainWindow, loyal_system_settings.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Reports(QMainWindow, report_page.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Equipment(QMainWindow, set_equipment_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Gamesessions(QMainWindow, set_gamesession_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Halls(QMainWindow, set_hall_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()