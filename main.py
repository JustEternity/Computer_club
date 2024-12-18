import sys
import datetime

import main_window
import create_client_window
import login_window
import loyal_system_settings
import report_page
import set_equipment_window
import set_gamesession_window
import set_hall_window

from decimal import Decimal

import dbrequests

from config import dbkey, dbpassword
from dbase import Database

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog, QListWidgetItem
from PyQt6.QtCore import QEvent, Qt, QDate, QTime
from PyQt6.QtGui import QFont, QPalette, QColor



class Comp_club_main(QMainWindow, main_window.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.id_client = {}
        self.id_hall = {}
        self.id_equip = {}
        self.id_gamesessions = {}
        self.id_reports = {}
        self.cur_hall = None
        self.busy_client = []
        self.busy_equip = []

        self.create_session_button.clicked.connect(self.open_gamesession_settings)
        self.loyal_system_button.clicked.connect(self.open_loyal_system_settings)
        self.create_client_button.clicked.connect(self.open_client_settings)
        self.create_equipment_button.clicked.connect(self.open_equipment_settings)
        self.list_of_clients.itemDoubleClicked.connect(self.update_client_info)
        self.list_of_reports.itemDoubleClicked.connect(self.check_report)
        self.list_of_equipment.itemDoubleClicked.connect(self.update_equipment_info)
        self.list_of_sessions.itemDoubleClicked.connect(self.update_sessions_info)


        self.tabWidget.resizeEvent = self.check_resize

        self.get_info()

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

    def add_gamesessions(self):
        self.list_of_sessions.clear()
        for row in self.gamesession_list:
            for i in self.equipment_list:
                if i['id'] == row['equipment'] and i['hall'] == self.cur_hall:
                    price = str(row['price']) + ' руб.'
                    item = QListWidgetItem(('ID сеанса: ' + str(row['id'])).center(15) + ' ' +
                                           ('ID клиента: ' + str(row['client'])).center(15) + ' ' +
                                           ('ID устройства: ' + str(row['equipment'])).center(20) + ' ' +
                                           ('Начало: ' + row['starttime'].strftime("%d.%m %H:%M")).center(22) + ' ' +
                                           ('Длительность: ' + str(row['duration'])).center(25) + ' ' + price.center(15))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.list_of_sessions.addItem(item)
                    self.id_gamesessions[self.list_of_sessions.count() - 1] = row['id']
                    self.busy_client.append(row['client'])
                    self.busy_equip.append(row['equipment'])

    def add_clients(self):
        self.list_of_clients.clear()
        for row in self.client_list:
            if row['secondname'] == 'None':
                sec = ' '
            else:
                sec = row['secondname']
            item = QListWidgetItem(('ID: ' + str(row['id'])).center(8) + row['name'].center(25) + ' ' + row['surname'].center(25) + ' ' + sec.center(25) + ' '
                                   + row['birthdate'].center(15) + ' ' + row['telephone'].center(15))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_of_clients.addItem(item)
            self.id_client[self.list_of_clients.count() - 1] = row['id']

    def add_equipments(self):
        self.list_of_equipment.clear()
        for row in self.equipment_list:
            for i in self.hall_list:
                if row['hall'] == i['id']:
                    hall = i['name']
            place = 'место ' + str(row['place'])
            price = str(row['price'])+ 'руб./час'
            item = QListWidgetItem(('ID:' + str(row['id'])).center(6) + ' ' + row['category'].center(25) + ' ' +
                                   str(hall).center(25) + ' ' + place.center(15) + ' ' + price.center(25))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_of_equipment.addItem(item)
            self.id_equip[self.list_of_equipment.count() - 1] = row['id']

    def get_info(self):
        self.gamesession_list = db.fetch_all(dbrequests.get_gamesession())
        self.client_list = db.fetch_all(dbrequests.get_client())
        self.client_list = db.decrypt_data(self.client_list)
        self.equipment_list = db.fetch_all(dbrequests.get_equipment())
        self.hall_list = db.fetch_all(dbrequests.get_hall())
        self.report_list = db.fetch_all(dbrequests.get_reports())

        self.add_clients()
        self.add_equipments()
        self.add_halls()
        self.add_reports()
        self.add_gamesessions()

    def add_reports(self):
        self.list_of_reports.clear()
        for i in self.report_list:
            item = QListWidgetItem(i['name'])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_of_reports.addItem(item)
            self.id_reports[self.list_of_reports.count()-1] = i['id']

    def add_halls(self):
        self.select_hall.clear()
        for i in self.hall_list:
            if self.select_hall.findText(i['name']) == -1:
                hall = i['name']
                self.select_hall.addItem(hall)
                self.id_hall[self.select_hall.count() - 1] = i['id']
        self.select_hall.addItem('+')

    def check_report(self, item):
        for i in self.report_list:
            if i['id'] == self.id_reports[self.list_of_reports.row(item)]:
                self.setEnabled(False)
                self.window = Reports(id=i['id'], name=i['name'], description=i['description'], parent=self)
                self.window.show()

    def update_client_info(self, item):
        for i in self.client_list:
            if i['id'] == self.id_client[self.list_of_clients.row(item)]:
                self.setEnabled(False)
                self.window = Clients(id=i['id'],
                                      name=i['name'],
                                      surname=i['surname'],
                                      secname=i['secondname'],
                                      tel=i['telephone'],
                                      dbirth=i['birthdate'],
                                      parent=self,
                                      update=True)
                self.window.show()

    def update_equipment_info(self, item):
        for i in self.equipment_list:
            if i['id'] == self.id_equip[self.list_of_equipment.row(item)]:
                self.setEnabled(False)
                self.window = Equipment(id=i['id'],
                                        category=i['category'],
                                        description=i['description'],
                                        hall=i['hall'],
                                        place=i['place'],
                                        price=i['price'],
                                        update=True,
                                        parent=self)
                self.window.show()

    def update_sessions_info(self, item):
        if self.cur_hall == None:
            return None
        for i in self.gamesession_list:
            if i['id'] == self.id_gamesessions[self.list_of_sessions.row(item)]:
                self.setEnabled(False)
                self.window = Gamesessions(id=i['id'],
                                           client=i['client'],
                                           equipment=i['equipment'],
                                           starttime=i['starttime'],
                                           duration=i['duration'],
                                           price=i['price'],
                                           update=True, hall=self.cur_hall, parent=self)
                self.window.show()

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonDblClick and source == self.line_edit:
            if self.line_edit.text() != '':
                self.open_holl_creating(self.line_edit.text())
            return True
        return super().eventFilter(source, event)

    def change_hall(self, index):
        if self.select_hall.currentText() == '+':
            self.open_holl_creating(None)
            self.select_hall.setCurrentIndex(-1)
        elif index != -1:
            self.cur_hall = self.id_hall[index]
            self.add_gamesessions()

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
        if self.cur_hall == None:
            return None
        self.setEnabled(False)
        self.window = Gamesessions(hall=self.cur_hall, parent=self)
        self.window.show()

    def open_loyal_system_settings(self):
        self.setEnabled(False)
        self.window = Loyal_system(parent=self)
        self.window.show()

    def open_client_settings(self):
        self.setEnabled(False)
        self.window = Clients(parent=self, update=False)
        self.window.show()

    def open_equipment_settings(self):
        self.setEnabled(False)
        self.window = Equipment(parent=self)
        self.window.show()

    def open_holl_creating(self, name):
        self.setEnabled(False)
        for i in self.hall_list:
            if name == i['name'] and name != '+':
                self.window = Halls(id=i['id'], name=i['name'], placecount=i['placecount'], update=True, parent=self)
                self.window.show()
        if name == None:
            self.window = Halls(parent=self)
            self.window.show()


class Clients(QMainWindow, create_client_window.Ui_MainWindow):
    def __init__(self, id=None, name=None, surname=None, secname=None, tel=None, dbirth=None, parent=None, update=False) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.id = id
        self.is_update = update

        self.surname = self.surname_edit.text()
        self.name = self.name_edit.text()
        self.secname = self.secondname_edit.text()
        self.tel = self.tel_edit.text()
        self.dbirth = self.datebirth_edit.date()

        if name and surname and secname and tel and dbirth:
            self.surname_edit.setText(surname)
            self.name_edit.setText(name)
            if secname != 'None':
                self.secondname_edit.setText(secname)
            else:
                self.secondname_edit.setText('')
            self.tel_edit.setText(tel)
            self.datebirth_edit.setDate(QDate.fromString(dbirth, "yyyy-MM-dd"))
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
        if self.surname!='' and self.name!='' and self.tel!='' and self.dbirth!='':
            if self.secname == '':
                self.secname = None
            if not self.is_update:
                query = dbrequests.add_client(db.encrypt(self.name),
                                              db.encrypt(self.surname),
                                              db.encrypt(self.secname),
                                              db.encrypt(self.dbirth.toString("yyyy-MM-dd")),
                                              db.encrypt(self.tel))
                db.execute_query(query)
                self.close()
            elif self.is_update:
                query = dbrequests.update_client(self.id,
                                                 db.encrypt(self.surname),
                                                 db.encrypt(self.name),
                                                 db.encrypt(self.secname),
                                                 db.encrypt(self.dbirth.toString("yyyy-MM-dd")),
                                                 db.encrypt(self.tel))
                db.execute_query(query)
                self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_client(self):
        if self.surname and self.name and self.tel and self.dbirth and self.id:
            query = dbrequests.del_client(self.id)
            db.execute_query(query)
            self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

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
            self.parent().get_info()
            self.id = self.parent().id_client
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
        self.settings = db.fetch_all(dbrequests.get_loyalsystem())
        self.write_in_table()
        self.condition_tab.itemChanged.connect(self.update_table)

    def update_table(self, item):
        try:
            if len(item.text()) > 5:
                self.show_warning('Слишком большое число')
                return None
            self.condition_tab.blockSignals(True)
            if  item.text() == '':
                if item.column() == 0:
                    self.settings[item.row()]['hourquantity'] = ''
                else:
                    self.settings[item.row()]['discount'] = ''
            else:
                if item.column() == 0:
                    self.settings[item.row()]['hourquantity'] = int(item.text())
                else:
                    self.settings[item.row()]['discount'] = int(item.text())
            self.write_in_table()
            self.condition_tab.blockSignals(False)
        except Exception as e:
            self.show_warning('Условием может быть только целое число')

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def write_in_table(self):
        self.settings = [k for k in self.settings if k]
        self.condition_tab.setRowCount(len(self.settings))
        for row, i in enumerate(self.settings):
            if 'hourquantity' in i.keys() and 'discount' in i.keys():
                item = QTableWidgetItem(str(i['hourquantity']))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.condition_tab.setItem(row, 0, item)
                item = QTableWidgetItem(f"{i['discount']}%" if 'discount' in i.keys() else '')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.condition_tab.setItem(row, 1, item)

    def add_new_condition(self):
        row = self.condition_tab.rowCount()
        self.condition_tab.insertRow(row)
        self.settings.append({'hourquantity': '', 'discount': ''})
        self.condition_tab.setCurrentCell(row, 0)
        self.condition_tab.setFocus()

    def closeEvent(self, event):
        if self.parent():
            db.execute_query('TRUNCATE TABLE loyalsystem;')
            for i in self.settings:
                if 'hourquantity' in i.keys() and 'discount' in i.keys():
                    if i['hourquantity'] != '' and i['discount'] != '':
                        db.execute_query(dbrequests.add_loyal_settings(i['hourquantity'], i['discount']))
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Reports(QMainWindow, report_page.Ui_MainWindow):
    def __init__(self, id=None, name=None, description=None, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.id = id
        self.id_report = self.parent().id_reports
        self.report_name.setText(name)
        self.report_description.setText(description)
        self.create_report_button.clicked.connect(self.save_report)

    def save_report(self):
        self.close()

    def closeEvent(self, event):
        if self.parent():
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Equipment(QMainWindow, set_equipment_window.Ui_MainWindow):
    def __init__(self, id=None, category=None, description=None, hall=None, place=None, price=None, update=False, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.id = id
        self.is_update = update
        self.id_hall = {}
        self.hall_list = self.parent().hall_list
        self.equip_list = self.parent().equipment_list

        self.fill_hall_selection()

        if id and self.is_update:
            self.hall = hall
            index = self.set_category_equip.findText(category)
            self.set_category_equip.setCurrentIndex(index)
            self.equip_description.setText(description)
            for row in self.equip_list:
                for i in self.hall_list:
                    if row['hall'] == i['id']:
                        halltmp = i['name']
            index = self.set_hall_equip.findText(halltmp)
            self.set_hall_equip.setCurrentIndex(index)
            self.fill_place_selection(self.hall, True)
            index = self.set_equip_place.findText(str(place))
            self.set_equip_place.setCurrentIndex(index)
            self.set_price_equip.setText(str(price))

        self.category = category
        self.hall = hall
        self.place = place
        self.description = self.equip_description.toPlainText()
        self.price = self.set_price_equip.text()

        self.set_category_equip.currentIndexChanged.connect(self.change_category)
        self.equip_description.textChanged.connect(self.change_description)
        self.set_hall_equip.currentIndexChanged.connect(self.change_hall)
        self.set_equip_place.currentIndexChanged.connect(self.change_place)
        self.set_price_equip.textChanged.connect(self.change_price)

        self.save_equip_button.clicked.connect(self.save_equip)
        self.del_equip_button.clicked.connect(self.del_equip)

    def change_place(self, index):
        self.place = self.set_equip_place.itemText(index)

    def fill_place_selection(self, hall_id, update=False):
        self.set_equip_place.clear()
        tmp = []
        if not update:
            tmp = []
            for k in self.equip_list:
                if k['hall'] == hall_id:
                    tmp.append(int(k['place']))
        for i in self.hall_list:
            if i['id'] == hall_id:
                for j in range(1, i['placecount']+1):
                    if j not in tmp:
                        self.set_equip_place.addItem(str(j))

    def fill_hall_selection(self):
        self.set_hall_equip.clear()
        for i in self.parent().hall_list:
            if self.set_hall_equip.findText(i['name']) == -1:
                hall = i['name']
                self.set_hall_equip.addItem(hall)
                self.id_hall[self.set_hall_equip.count() - 1] = i['id']

    def save_equip(self):
        for i in self.hall_list:
            if i['name'] == self.hall:
                self.hall = i['id']
        if self.category and self.description and self.hall and self.place and self.price:
            if not self.is_update:
                query = dbrequests.add_equipment(self.category, self.description, self.hall, self.price, self.place)
                db.execute_query(query)
                self.close()
            else:
                query = dbrequests.update_equip(self.id, self.category, self.description, self.hall, self.price, self.place)
                db.execute_query(query)
                self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_equip(self):
        query = dbrequests.del_equipment(self.id)
        db.execute_query(query)
        self.close()

    def change_category(self, index):
        self.category = self.set_category_equip.itemText(index)

    def change_description(self):
        if len(self.equip_description.toPlainText()) > 300:
            self.equip_description.textCursor().deletePreviousChar()
        self.description = self.equip_description.toPlainText()

    def change_hall(self, index):
        self.hall = self.set_hall_equip.itemText(index)
        self.fill_place_selection(self.id_hall[index])

    def change_price(self, text):
        self.price = text

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event):
        if self.parent():
            self.parent().get_info()
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Gamesessions(QMainWindow, set_gamesession_window.Ui_MainWindow):
    def __init__(self, id=None, client=None, equipment=None, starttime=None,
                 duration=None, price=None, update=False, hall=None, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.is_update = update
        self.id = id
        self.equip_list = self.parent().equipment_list
        self.client_list = self.parent().client_list
        self.id_equip = self.parent().id_equip
        self.id_client = self.parent().id_client
        self.loyal_list = db.fetch_all(dbrequests.get_loyalsystem())
        self.busy_clients = self.parent().busy_client
        self.busy_equip = self.parent().busy_equip
        self.current_hall = hall
        self.starttime = starttime
        self.current_equip = {}
        self.current_client = {}

        self.fill_client_equip_selection()

        if self.id and self.is_update:
            index = self.set_client.findText(str(client))
            self.set_client.setCurrentIndex(index)
            index = self.set_equipment.findText(str(equipment))
            self.set_equipment.setCurrentIndex(index)
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            formatted_duration = f"{int(hours):02d}:{int(minutes):02d}"
            qtime = QTime.fromString(formatted_duration, "HH:mm")
            self.time_session_edit.setTime(qtime)
            self.price_session.setText(str(price))
            for i in self.equip_list:
                if i['id'] == equipment:
                    self.equipment_info.setText(i['description'])

        self.client = client
        self.equip = equipment
        self.time_session = duration
        self.price = price
        self.description = self.equipment_info.toPlainText()

        self.set_client.currentIndexChanged.connect(self.change_client)
        self.set_equipment.currentIndexChanged.connect(self.change_equip)
        self.time_session_edit.timeChanged.connect(self.change_duration)

        self.save_session_button.clicked.connect(self.save_gamesession)
        self.stop_session_button.clicked.connect(self.stop_gamesession)

    def fill_client_equip_selection(self):
        if not self.is_update:
            for i in self.client_list:
                if i['id'] not in self.busy_clients:
                    self.set_client.addItem(str(i['id']))
                    self.current_client[self.set_client.count()-1] = i['id']
            for j in self.equip_list:
                if j['id'] not in self.busy_equip and j['hall'] == self.current_hall:
                    self.set_equipment.addItem(str(j['id']))
                    self.current_equip[self.set_equipment.count()-1] = j['id']
        else:
            self.set_client.setEnabled(False)
            self.set_equipment.setEnabled(False)
            for i in self.client_list:
                self.set_client.addItem(str(i['id']))
                self.current_client[self.set_client.count()-1] = i['id']
            for j in self.equip_list:
                self.set_equipment.addItem(str(j['id']))
                self.current_equip[self.set_equipment.count()-1] = j['id']

    def save_gamesession(self):
        if self.starttime == None:
            self.starttime = datetime.datetime.now()
            self.starttime = self.starttime.strftime("%Y-%m-%d %H:%M")

        if self.id and self.client and self.equip and self.starttime and self.time_session and self.price and Decimal(self.price) > 0:
            if self.is_update:
                query = dbrequests.update_gamesession(self.id, self.client, self.equip, self.starttime, self.time_session, self.price)
                db.execute_query(query)
                self.close()
            else:
                self.busy_clients.append(self.client)
                self.busy_equip.append(self.equip)
                query = dbrequests.add_gamesession(self.client, self.equip, self.starttime, self.time_session, self.price)
                db.execute_query(query)
                self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def stop_gamesession(self):
        if self.id and self.client and self.equip and self.starttime and self.time_session and self.price:
            query = dbrequests.del_gamesession(self.id)
            db.execute_query(query)
            self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def change_client(self, index):
        self.client = self.set_client.itemText(index)
        self.client = self.current_client[index]

    def change_equip(self, index):
        self.equip = self.set_equipment.itemText(index)
        for i in self.equip_list:
                if i['id'] == self.current_equip[index]:
                    self.equipment_info.setText(i['description'])
                    tmp = i['id']
        if self.time_session:
            self.calculate_price_session(self.time_session, tmp, self.id)

    def change_duration(self, time):
        self.time_session = time.toString('HH:mm')
        if self.equip:
            for i in self.equip_list:
                if i['id'] == int(self.equip):
                    tmp = i['id']
            self.calculate_price_session(self.time_session, tmp, self.id)

    def calculate_price_session(self, time, equip, id):
        for i in self.equip_list:
            if i['id'] == int(equip):
                equip_price = i['price']
        query = dbrequests.get_client_hours(id)
        res = db.execute_and_fetch(query)['SEC_TO_TIME(SUM(TIME_TO_SEC(duration)))']
        if res == None:
            sum_time = datetime.datetime.strptime('00:00', '%H:%M').time()
        else:
            hours, remainder = divmod(res.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            formatted_duration = f"{int(hours):02d}:{int(minutes):02d}"
            qtime = QTime.fromString(formatted_duration, "HH:mm")
            sum_time = datetime.datetime.strptime(qtime, '%H:%M').time()
        sum_hour = sum_time.hour
        disc = 0
        for k in self.loyal_list:
            if disc < k['hourquantity'] <= sum_hour:
                disc = k['discount']
        cur_time = datetime.datetime.strptime(time, '%H:%M').time()
        time_min = cur_time.minute
        if time_min >= 30:
            cur_time = Decimal(cur_time.hour+1)
            discount = Decimal(1 - (disc / 10))
            self.price_session.setText(str(equip_price* (cur_time) * (discount)))
            self.price = self.price_session.text()
        else:
            cur_time = Decimal(cur_time.hour)
            discount = Decimal(1 - (disc / 10))
            self.price_session.setText(str(equip_price*(cur_time) * (discount)))
            self.price = self.price_session.text()

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event):
        self.set_client.setEnabled(True)
        self.set_equipment.setEnabled(True)
        if self.parent():
            self.parent().get_info()
            self.parent().setEnabled(True)
        super().closeEvent(event)


class Halls(QMainWindow, set_hall_window.Ui_MainWindow):
    def __init__(self, id=None, name=None, placecount=None, update=False, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.id = id
        self.is_update = update

        self.name = self.hallname_edit.text()
        self.placecount = self.roominess_hall_edit.text()
        if id and name and placecount:
            self.hallname_edit.setText(name)
            self.roominess_hall_edit.setText(str(placecount))
            self.name = self.hallname_edit.text()
            self.placecount = self.roominess_hall_edit.text()

        self.hallname_edit.textChanged.connect(self.change_hallname)
        self.roominess_hall_edit.textChanged.connect(self.change_placecount)
        self.hall_save_button.clicked.connect(self.save_hall)
        self.hall_del_button.clicked.connect(self.del_hall)

    def save_hall(self):
        if self.name and self.placecount:
            if not self.is_update:
                query = dbrequests.add_hall(self.name, str(self.placecount))
                db.execute_query(query)
                self.close()
            else:
                query = dbrequests.update_hall(self.id, self.name, str(self.placecount))
                db.execute_query(query)
                self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_hall(self):
        if self.name and self.placecount:
            query = dbrequests.del_hall(self.id)
            db.execute_query(query)
            self.close()
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def change_hallname(self, text):
        self.name = text

    def change_placecount(self, text):
        self.placecount = text

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event):
        self.parent().get_info()
        self.parent().add_halls()
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

