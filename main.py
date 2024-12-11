import sys

import main_window
import create_client_window
import login_window
import loyal_system_settings
import report_page
import set_equipment_window
import set_gamesession_window
import set_hall_window

import dbrequests

from config import dbkey, dbpassword
from dbase import Database

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QFont, QPalette, QColor



class Comp_club_main(QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, db) -> None:
        super().__init__()
        self.setupUi(self)

        self.db = db
        self.create_session_button.clicked.connect(self.open_gamesession_settings)
        self.loyal_system_button.clicked.connect(self.open_loyal_system_settings)
        self.create_client_button.clicked.connect(self.open_client_settings)
        self.create_equipment_button.clicked.connect(self.open_equipment_settings)

        self.tabWidget.resizeEvent = self.check_resize

        self.list_of_reports.addItem('test1')
        self.list_of_reports.addItem('test2')
        self.list_of_reports.addItem('test3')

        self.select_hall.addItem('+')
        self.select_hall.currentIndexChanged.connect(self.change_hall)
        self.select_hall.setEditable(True)
        self.line_edit = self.select_hall.lineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setPlaceholderText('Зал')
        font = QFont("Bahnschrift SemiLight SemiConde", 14)
        self.line_edit.setFont(font)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Text, QColor("white"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("white"))
        self.line_edit.setPalette(palette)
        self.line_edit.installEventFilter(self)


    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonDblClick and source == self.line_edit:
            if self.line_edit.text() != '':
                self.open_holl_creating()
            return True
        return super().eventFilter(source, event)

    def change_hall(self):
        if self.select_hall.currentText() == '+':
            self.open_holl_creating()
            self.select_hall.setCurrentIndex(-1)

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

    def open_holl_creating(self):
        self.setEnabled(False)
        self.window = Halls(self)
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
    def __init__(self, db, admins) -> None:
        super().__init__()
        self.setupUi(self)

        self.db = db
        self.admins = admins
        self.login = self.edit_login.text()
        self.password = self.edit_password.text()
        self.edit_login.textChanged.connect(self.change_login)
        self.edit_password.textChanged.connect(self.change_password)
        self.login_button.clicked.connect(self.start_app)


    def start_app(self):
        for admin in self.admins:
            if admin['adminlogin'] == self.login and admin['adminpassword'] == self.password:
                self.window = Comp_club_main(self.db)
                self.window.show()
                self.close()
                break
        else:
            self.show_warning("Неверный логин или пароль!")

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


    def change_login(self, text):
        self.login = text

    def change_password(self, text):
        self.password = text


class Loyal_system(QMainWindow, loyal_system_settings.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.add_condition_button.clicked.connect(self.add_new_condition)

    def add_new_condition(self):
        row = self.condition_tab.rowCount()
        self.condition_tab.insertRow(row)
        self.condition_tab.setCurrentCell(row, 0)
        self.condition_tab.setFocus()

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
    db = Database('localhost', 'root', dbpassword, 'computerclub', dbkey)
    users = db.fetch_all(dbrequests.get_admin())
    users = db.decrypt_data(users)
    app = QApplication(sys.argv)
    window = Login(db, users)
    window.show()
    app.exec()
    db.close()



if __name__ == "__main__":
    main()

