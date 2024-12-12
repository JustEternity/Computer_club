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

        self.surname = self.surname_edit.text()
        self.name = self.name_edit.text()
        self.secname = self.secondname_edit.text()
        self.tel = self.tel_edit.text()
        self.dbirth = self.datebirth_edit.date()

        self.surname_edit.textChanged.connect(self.change_surname)
        self.name_edit.textChanged.connect(self.change_name)
        self.secondname_edit.textChanged.connect(self.change_secname)
        self.tel_edit.textChanged.connect(self.change_telephone)
        self.datebirth_edit.dateChanged.connect(self.change_datebirth)

        self.save_client_button.clicked.connect(self.save_client)
        self.del_client_button.clicked.connect(self.del_client)



    def save_client(self):
        if self.surname and self.name and self.tel and self.dbirth:
            if self.secname == '':
                self.secname = None
            print(self.name, self.surname, self.secname, self.tel, self.dbirth, sep=' ')
            # query = dbrequests.add_client(self.db.encrypt(self.name), self.db.encrypt(self.surname), self.db.encrypt(self.secname), self.db.encrypt(self.dbirth), self.db.encrypt(self.tel))
            # self.db.execute_query(query)
            self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_client(self):
        # if self.surname and self.name and self.tel and self.dbirth and self.id:
        self.close()
            # query = dbrequests.del_client(self.id)
            # self.db.execute_query(query)
        # else:
        #     self.show_warning("Присутствуют незаполненные поля!")

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def change_surname(self, text):
        self.surname = text

    def change_name(self, text):
        self.name = text

    def change_secname(self, text):
        self.secname = text

    def change_telephone(self, text):
        self.tel = text

    def change_datebirth(self, date):
        self.dbirth = date

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Login(QMainWindow, login_window.Ui_MainWindow):
    def __init__(self, admins) -> None:
        super().__init__()
        self.setupUi(self)

        self.admins = admins
        self.login = self.edit_login.text()
        self.password = self.edit_password.text()
        self.edit_login.textChanged.connect(self.change_login)
        self.edit_password.textChanged.connect(self.change_password)
        self.login_button.clicked.connect(self.start_app)


    def start_app(self):
        for admin in self.admins:
            if admin['adminlogin'] == self.login and admin['adminpassword'] == self.password:
                self.window = Comp_club_main()
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

        self.name = self.report_name.text()
        self.description = self.report_description.toPlainText()

        self.create_report_button.clicked.connect(self.save_report)

    def save_report(self):
        pass

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Equipment(QMainWindow, set_equipment_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.category = self.set_category_equip.currentData()
        self.description = self.equip_description.toPlainText()
        self.hall = self.set_hall_equip.currentData()
        self.place = self.set_equip_place.currentData()
        self.price = self.set_price_equip.text()

        self.set_category_equip.currentIndexChanged.connect(self.change_category)
        self.equip_description.textChanged.connect(self.change_description)
        self.set_hall_equip.currentIndexChanged.connect(self.change_hall)
        self.set_equip_place.currentIndexChanged.connect(self.change_place)
        self.set_price_equip.textChanged.connect(self.change_price)

        self.save_equip_button.clicked.connect(self.save_equip)
        self.del_equip_button.clicked.connect(self.del_equip)

    def save_equip(self):
        print(self.category, self.description, self.hall, self.place, self.price)
        self.close()

    def del_equip(self):
        self.close()

    def change_category(self, index):
        self.category = self.set_category_equip.itemText(index)

    def change_description(self):
        self.description = self.equip_description.toPlainText()

    def change_hall(self, index):
        self.hall = self.set_hall_equip.itemText(index)

    def change_place(self, index):
        self.place = self.set_equip_place.itemText(index)

    def change_price(self, text):
        self.price = text

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Gamesessions(QMainWindow, set_gamesession_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.client = self.set_client.currentData()
        self.equip = self.set_equipment.currentData()
        self.description = self.equipment_info.toPlainText()
        self.time_session = self.time_session_edit.time()
        self.price = self.price_session.text()

        self.set_client.currentIndexChanged.connect(self.change_client)
        self.set_equipment.currentIndexChanged.connect(self.change_equip)
        self.time_session_edit.timeChanged.connect(self.change_duration)

        self.save_session_button.clicked.connect(self.save_gamesession)
        self.stop_session_button.clicked.connect(self.stop_gamesession)

    def save_gamesession(self):
        print(self.client, self.equip, self.equipment_info.toPlainText(), self.time_session, self.price)
        self.close()

    def stop_gamesession(self):
        self.close()

    def change_client(self, index):
        self.client = self.set_client.itemText(index)

    def change_equip(self, index):
        self.equip = self.set_equipment.itemText(index)

    def change_duration(self, time):
        self.time_session = time

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Halls(QMainWindow, set_hall_window.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.name = self.hallname_edit.text()
        self.placecount = self.roominess_hall_edit.text()

        self.hallname_edit.textChanged.connect(self.change_hallname)
        self.roominess_hall_edit.textChanged.connect(self.change_placecount)
        self.hall_save_button.clicked.connect(self.save_hall)
        self.hall_del_button.clicked.connect(self.del_hall)

    def save_hall(self):
        print(self.name, self.placecount)
        self.close()

    def del_hall(self):
        self.close()

    def change_hallname(self, text):
        self.name = text

    def change_placecount(self, text):
        self.placecount = text

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


def main():
    users = db.fetch_all(dbrequests.get_admin())
    users = db.decrypt_data(users)
    app = QApplication(sys.argv)
    window = Login(users)
    window.show()
    app.exec()
    db.close()



if __name__ == "__main__":
    db = Database('localhost', 'root', dbpassword, 'computerclub', dbkey)
    main()

