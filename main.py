import sys
import datetime
import pymysql

import main_window
import create_client_window
import login_window
import loyal_system_settings
import report_page
import set_equipment_window
import set_gamesession_window
import set_hall_window

from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import dbrequests

from config import dbkey, dbpassword
from dbase import Database

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog, QListWidgetItem
from PyQt6.QtCore import QEvent, Qt, QDate, QTime, QTimer
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
        self.checked = None
        self.busy_client = []
        self.busy_equip = []
        self.session_filter = self.find_game_session.text()
        self.client_filter = self.find_client.text()
        self.equip_filter = self.find_equipment.text()
        self.opened_form = False

        self.create_session_button.clicked.connect(self.open_gamesession_settings)
        self.loyal_system_button.clicked.connect(self.open_loyal_system_settings)
        self.create_client_button.clicked.connect(self.open_client_settings)
        self.create_equipment_button.clicked.connect(self.open_equipment_settings)
        self.list_of_clients.itemDoubleClicked.connect(self.update_client_info)
        self.list_of_reports.itemDoubleClicked.connect(self.check_report)
        self.list_of_equipment.itemDoubleClicked.connect(self.update_equipment_info)
        self.list_of_sessions.itemDoubleClicked.connect(self.update_sessions_info)
        self.find_game_session.textChanged.connect(self.change_session_filter)
        self.find_client.textChanged.connect(self.change_client_filter)
        self.find_equipment.textChanged.connect(self.change_equipment_filter)
        self.list_of_clients.itemClicked.connect(self.choose_client)

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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_sessions)
        self.timer.start(10000)

    def choose_client(self, item):
        index = self.list_of_clients.row(item)
        self.checked = self.id_client[index]

    def check_sessions(self):
        current_time = datetime.datetime.now()
        query = dbrequests.get_gamesession()
        sessions = db.fetch_all(query)

        for session in sessions:
            start_time = session['starttime']
            if isinstance(start_time, str):
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

            duration = session['duration']
            if isinstance(duration, str):
                h, m, s = map(int, duration.split(':'))
                duration = datetime.timedelta(hours=h, minutes=m, seconds=s)

            end_time = start_time + duration
            if (current_time >= end_time) and session['completed'] == 0:
                self.open_edit_form(session['id'], session['client'], session['equipment'],
                                    session['starttime'], session['duration'], session['price'])

    def open_edit_form(self, session_id, session_client, session_equipment,
                    session_starttime, session_duration, session_price):
        if not self.opened_form:
            window = Gamesessions(id=session_id,
                                    client=session_client,
                                    equipment=session_equipment,
                                    starttime=session_starttime,
                                    duration=session_duration,
                                    price=session_price,
                                    update=True, hall=self.cur_hall, parent=self)
            window.show()
            self.opened_form = True

    def add_gamesessions(self):
        self.busy_client.clear()
        self.busy_equip.clear()
        for j in self.gamesession_list:
            for i in self.equipment_list:
                if i['id'] == j['equipment'] and j['completed'] == 0:
                    self.busy_client.append(j['client']) if j['client'] not in self.busy_client else None
                    self.busy_equip.append(j['equipment']) if  j['equipment'] not in self.busy_equip else None
        self.list_of_sessions.clear()
        for row in self.gamesession_list:
            for i in self.equipment_list:
                if row['completed'] == 0 and i['id'] == row['equipment'] and i['hall'] == self.cur_hall and (str(self.session_filter) in str(row['equipment']) or str(self.session_filter) in str(row['client'])):
                    price = str(row['price']) + ' руб.'
                    total_seconds = int(row['duration'].total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    item = QListWidgetItem(('ID сеанса: ' + str(row['id'])).center(15) + ' ' +
                                           ('ID клиента: ' + str(row['client'])).center(15) + ' ' +
                                           ('ID устройства: ' + str(row['equipment'])).center(20) + ' ' +
                                           ('Начало: ' + row['starttime'].strftime("%d.%m %H:%M")).center(22) + ' ' +
                                           ('Длительность: ' + f"{hours:02}:{minutes:02}").center(25) + ' ' + price.center(15))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.list_of_sessions.addItem(item)
                    self.id_gamesessions[self.list_of_sessions.count() - 1] = row['id']
                    self.busy_client.append(row['client']) if row['client'] not in self.busy_client else None
                    self.busy_equip.append(row['equipment']) if row['equipment'] not in self.busy_equip else None

    def add_clients(self):
        self.list_of_clients.clear()
        for row in self.client_list:
            if row['secondname'] == 'None':
                sec = ' '
            else:
                sec = row['secondname']
            if self.client_filter in row['surname'] or self.client_filter in row['telephone']:
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
            if row['id'] in self.busy_equip:
                access = 'Занят'
            else:
                access = 'Доступен'
            if self.equip_filter in str(row['id']) or self.equip_filter in hall or self.equip_filter in access:
                place = 'место ' + str(row['place'])
                price = str(row['price']) + ' руб./час'
                item = QListWidgetItem(('ID:' + str(row['id'])).center(6) + ' ' + row['category'].center(25) + ' ' +
                                    str(hall).center(25) + ' ' + place.center(15) + ' ' + price.center(25) + ' ' + access.center(12))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.list_of_equipment.addItem(item)
                self.id_equip[self.list_of_equipment.count() - 1] = row['id']

    def get_info(self):
        try:
            self.gamesession_list = db.fetch_all(dbrequests.get_gamesession())
            self.client_list = db.fetch_all(dbrequests.get_client())
            self.client_list = db.decrypt_data(self.client_list)
            self.equipment_list = db.fetch_all(dbrequests.get_equipment())
            self.hall_list = db.fetch_all(dbrequests.get_hall())
            self.report_list = db.fetch_all(dbrequests.get_reports())
        except (Exception, pymysql.Error) as e:
            self.show_warning('Ошибка получения данных, проверьте подключение')

        self.add_halls()
        self.add_reports()
        self.add_clients()
        self.add_gamesessions()
        self.add_equipments()

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
                self.window = Reports(id=i['id'], name=i['name'], description=i['description'], query=i['request'], report=self.id_reports[self.list_of_reports.row(item)], parent=self)
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
                self.cur_hall = None
            return True
        return super().eventFilter(source, event)

    def change_hall(self, index):
        if self.select_hall.currentText() == '+':
            self.open_holl_creating(None)
            self.select_hall.setCurrentIndex(-1)
            self.cur_hall = None
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

    def change_session_filter(self, text):
        self.session_filter = text
        self.add_gamesessions()

    def change_client_filter(self, text):
        self.client_filter = text
        self.add_clients()

    def change_equipment_filter(self, text):
        self.equip_filter = text
        self.add_equipments()

    def open_gamesession_settings(self):
        if self.cur_hall == None:
            return None
        self.setEnabled(False)
        self.window = Gamesessions(hall=self.cur_hall, parent=self)
        self.window.show()
        self.cur_hall = None

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

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


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
        self.client_list = self.parent().client_list

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
        if self.is_update == False:
            for i in self.client_list:
                if i['telephone'] == self.tel:
                    self.show_warning("Клиент с таким номером телефона уже зарегистрирован!")
                    return None
        if self.surname!='' and self.name!='' and self.tel!='' and self.dbirth!='':
            if self.secname == '':
                self.secname = None
            try:
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
            except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_client(self):
        if self.surname and self.name and self.tel and self.dbirth and self.id:
            try:
                query = dbrequests.del_client(self.id)
                db.execute_query(query)
                self.close()
            except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')
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
        self.surname = text.lstrip().rstrip()

    def change_name(self, text):
        self.name = text.lstrip().rstrip()

    def change_secname(self, text):
        self.secname = text.lstrip().rstrip()

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
            for i in self.settings:
                if i['hourquantity'] != '' and i['discount'] != '':
                    if (str(i['hourquantity']) == item.text() and item.column() == 0) or (str(i['discount']) == item.text() and item.column() == 1):
                        self.show_warning('Условия не могут повторяться!')
                        item.setText('')
                        return None
            if item.text() == '':
                if item.column() == 0:
                    self.settings[item.row()]['hourquantity'] = ''
                else:
                    self.settings[item.row()]['discount'] = ''
            else:
                if item.column() == 0:
                    self.settings[item.row()]['hourquantity'] = int(item.text())
                else:
                    self.settings[item.row()]['discount'] = int(item.text())
                if item.column() == 1 and (int(item.text()) > 100 or int(item.text()) < 0):
                    self.show_warning('Некорректный размер скидки')
                    item.setText('')
            self.condition_tab.blockSignals(True)
            self.write_in_table()
            self.condition_tab.blockSignals(False)
        except ValueError:
            self.show_warning('Условием может быть только целое число')
            item.setText('')
        except Exception as e:
            self.show_warning('Произошла ошибка')
            item.setText('')

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
    def __init__(self, id=None, name=None, description=None, query=None, report=None, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.id = id
        self.name = name
        self.description = description
        self.query = query
        self.report = report
        self.choose_client = self.parent().checked
        self.report_name.setText(name)
        self.report_description.setText(description)
        self.create_report_button.clicked.connect(self.save_report)


    def save_report(self, item):
        query = self.query
        try:
            match self.report:
                case 1:
                    res = db.execute_and_fetch(query)
                    self.attendance_to_pdf(arr=res)
                case 2:
                    res = db.execute_and_fetch(query=query, many=True)
                    self.popularity_to_pdf(arr=res)
                case 3:
                    res = db.execute_and_fetch(query=query, many=True)
                    self.av_time(arr=res)
                case 4:
                    if self.choose_client != None and self.choose_client != -1:
                        query = query.replace('{}', str(self.choose_client))
                        res = db.execute_and_fetch(query=query, many=True)
                        self.history_client(arr=res, client=self.choose_client)
                case 5:
                    res = db.execute_and_fetch(query=query, many=True)
                    self.hall_fullness(arr=res)
        except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')


    def attendance_to_pdf(self, arr=None):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(caption="Сохранить файл как", filter="PDF files (*.pdf)")

        if file_path:
            pdfmetrics.registerFont(TTFont('FreeFont', 'GNU Free Font/FreeSans.ttf'))

            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            c.setFont("FreeFont", 12)
            c.drawString(100, height - 40, "Отчет по работе компьютерного клуба за месяц")
            c.drawString(100, height - 80, f"Количество уникальных пользователей: {arr['Количество уникальных пользователей']}")
            c.drawString(100, height - 100, f"Количество игровых сессий: {arr['Количество игровых сессий']}")
            c.save()
        self.close()

    def popularity_to_pdf(self, arr=None):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(caption="Сохранить файл как", filter="PDF files (*.pdf)")

        if file_path:
            pdfmetrics.registerFont(TTFont('FreeFont', 'GNU Free Font/FreeSans.ttf'))
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            c.setFont("FreeFont", 12)
            c.drawString(100, height - 40, "Отчет по популярности оборудования")
            y_position = height - 80
            for result in arr:
                c.drawString(100, y_position, f"Категория: {result['category']}")
                c.drawString(100, y_position - 20, f"ID: {result['id']}")
                c.drawString(100, y_position - 40, f"Общее время аренды: {result['total_rental_time']}")
                c.drawString(100, y_position - 60, f"Количество сессий: {result['session_count']}")
                y_position -= 100
                if y_position < 100:
                    c.showPage()
                    c.setFont("FreeFont", 12)
                    y_position = height - 40
            c.save()
        self.close()

    def av_time(self, arr=None):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(caption="Сохранить файл как", filter="PDF files (*.pdf)")

        if file_path:
            pdfmetrics.registerFont(TTFont('FreeFont', 'GNU Free Font/FreeSans.ttf'))

            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            c.setFont("FreeFont", 12)
            c.drawString(100, height - 40, "Отчет по среднему времени аренды оборудования")

            y_position = height - 80
            for result in arr:
                if isinstance(result, dict):
                    c.drawString(100, y_position, f"Код устройства: {result.get('Код устройства', 'N/A')}")
                    c.drawString(100, y_position - 20, f"Общее время аренды: {int(result.get('Общее время аренды', 'N/A'))} минут")
                    c.drawString(100, y_position - 40, f"Количество проведенных сессий: {result.get('Количество проведенных сессий', 'N/A')}")
                    y_position -= 100

                    if y_position < 100:
                        c.showPage()
                        c.setFont("FreeFont", 12)
                        y_position = height - 40
                else:
                    print("Произошла ошибка при формировании отчета")

            c.save()
        self.close()

    def history_client(self, client=None, arr=None):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(caption="Сохранить файл как", filter="PDF files (*.pdf)")

        if file_path:
            pdfmetrics.registerFont(TTFont('FreeFont', 'GNU Free Font/FreeSans.ttf'))

            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            c.setFont("FreeFont", 12)
            c.drawString(100, height - 40, f"Отчет по игровым сессиям клиента {self.choose_client}")

            y_position = height - 80
            for result in arr:
                if isinstance(result, dict):
                    c.drawString(100, y_position, f"id сеанса: {result.get('id сеанса', 'N/A')}")
                    c.drawString(100, y_position - 20, f"id оборудования: {result.get('id оборудования', 'N/A')}")
                    c.drawString(100, y_position - 40, f"Время начала сеанса: {result.get('Время начала сеанса', 'N/A')}")
                    c.drawString(100, y_position - 60, f"Время аренды: {result.get('Время аренды', 'N/A')}")
                    c.drawString(100, y_position - 80, f"Цена: {result.get('Цена', 'N/A')}")
                    y_position -= 140

                    if y_position < 100:
                        c.showPage()
                        c.setFont("FreeFont", 12)
                        y_position = height - 40
                else:
                    print("Неверный формат данных: ожидается словарь")

            c.save()
        self.close()

    def hall_fullness(self, arr=None):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(caption="Сохранить файл как", filter="PDF files (*.pdf)")

        if file_path:
            pdfmetrics.registerFont(TTFont('FreeFont', 'GNU Free Font/FreeSans.ttf'))

            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            c.setFont("FreeFont", 12)
            c.drawString(100, height - 40, "Отчет по заполненности залов")

            y_position = height - 80
            printed_halls = set()

            for result in arr:
                if isinstance(result, dict):
                    hall_name = result.get('Зал', 'N/A')
                    if hall_name not in printed_halls:
                        c.drawString(100, y_position - 20, f"Зал: {hall_name}")
                        c.drawString(100, y_position - 40, f"Количество мест: {result.get('Количество мест', 'N/A')}")
                        printed_halls.add(hall_name)
                        y_position -= 80

                    c.drawString(100, y_position, f"Место: {result.get('Место', 'N/A')}")
                    c.drawString(100, y_position - 20, f"id устройства: {result.get('id устройства', 'N/A')}")
                    c.drawString(100, y_position - 40, f"Категория: {result.get('Категория', 'N/A')}")
                    y_position -= 60

                    if y_position < 100:
                        c.showPage()
                        c.setFont("FreeFont", 12)
                        y_position = height - 40
                else:
                    print("Произошла ошибка при формировании отчета")

            c.save()
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
        self.place = place
        self.id_hall = {}
        self.hall_list = self.parent().hall_list
        self.equip_list = self.parent().equipment_list

        self.fill_hall_selection()

        if self.id and self.is_update:
            self.hall = hall
            index = self.set_category_equip.findText(category)
            self.set_category_equip.setCurrentIndex(index)
            self.equip_description.setText(description)
            for i in self.hall_list:
                if self.hall == i['id']:
                    halltmp = i['name']
            index = self.set_hall_equip.findText(halltmp)
            self.set_hall_equip.setCurrentIndex(index)
            self.fill_place_selection(hall_id=self.hall, update=True)
            index = self.set_equip_place.findText(str(place))
            self.set_equip_place.setCurrentIndex(index)
            self.set_price_equip.setText(str(price))

        self.category = category
        self.hall = hall
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
            for k in self.equip_list:
                if k['hall'] == hall_id:
                    tmp.append(int(k['place']))
        else:
            for k in self.equip_list:
                if k['hall'] == hall_id and k['place'] != self.place:
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
        if self.category and self.description and self.hall and self.place and self.price != '.':
            try:
                if not self.is_update:
                    query = dbrequests.add_equipment(self.category, self.description, self.hall, self.price, self.place)
                    db.execute_query(query)
                    self.close()
                else:
                    query = dbrequests.update_equip(self.id, self.category, self.description, self.hall, self.price, self.place)
                    db.execute_query(query)
                    self.close()
            except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_equip(self):
        try:
            query = dbrequests.del_equipment(self.id)
            db.execute_query(query)
            self.close()
        except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')

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
        self.equip_list = db.fetch_all(dbrequests.get_equipment())
        self.client_list = db.fetch_all(dbrequests.get_client())
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
        self.time_session = self.time_session_edit.time().toString('HH:mm')
        self.price = price
        self.description = self.equipment_info.toPlainText()

        self.set_client.currentIndexChanged.connect(self.change_client)
        self.set_equipment.currentIndexChanged.connect(self.change_equip)
        self.time_session_edit.timeChanged.connect(self.change_duration)

        self.save_session_button.clicked.connect(self.save_gamesession)
        self.stop_session_button.clicked.connect(self.stop_gamesession)

        if not self.is_update:
            self.stop_session_button.setText('Отмена')

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
        if self.client and self.equip and self.starttime and self.time_session and self.price and Decimal(self.price) > 0:
            try:
                if self.is_update:
                    query = dbrequests.update_gamesession(self.id, self.client, self.equip, self.starttime, self.time_session, self.price)
                    db.execute_query(query)
                    self.close()
                else:
                    query = dbrequests.add_gamesession(self.client, self.equip, self.starttime, self.time_session, self.price)
                    db.execute_query(query)
                    self.busy_clients.append(self.client)
                    self.busy_equip.append(self.equip)
                    self.close()
            except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def stop_gamesession(self):
        if self.stop_session_button.text() == 'Отмена':
            self.close()
        else:
            try:
                if self.id and self.client and self.equip and self.starttime and self.time_session and self.price:
                    query = dbrequests.stop_gamesession(self.id)
                    db.execute_query(query)
                    self.close()
                else:
                    self.show_warning("Присутствуют незаполненные поля!")
            except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')

    def change_client(self, index):
        self.client = self.set_client.itemText(index)
        self.id = self.current_client[index]
        if self.time_session and self.equip:
            self.calculate_price_session(self.time_session, self.equip, self.id)

    def change_equip(self, index):
        self.equip = self.set_equipment.itemText(index)
        for i in self.equip_list:
                if i['id'] == self.current_equip[index]:
                    self.equipment_info.setText(i['description'])
                    tmp = i['id']
        if self.time_session  and self.client:
            self.calculate_price_session(self.time_session, tmp, self.id)

    def change_duration(self, time):
        self.time_session = time.toString('HH:mm')
        if self.equip and self.client:
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
            # qtime = QTime.fromString(formatted_duration, "HH:mm")
            sum_time = datetime.datetime.strptime(formatted_duration, '%H:%M').time()
        sum_hour = sum_time.hour
        disc = 0
        for k in self.loyal_list:
            if k['hourquantity'] <= sum_hour and k['discount'] > disc:
                disc = k['discount']
        cur_time = datetime.datetime.strptime(time, '%H:%M').time()
        time_min = cur_time.minute
        if time_min >= 30:
            cur_time = Decimal(cur_time.hour+1)
            discount = Decimal(1 - (disc / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.price_session.setText(f"{equip_price *cur_time * discount:.2f}")
            self.price = self.price_session.text()
        else:
            cur_time = Decimal(cur_time.hour)
            discount = Decimal(1 - (disc / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.price_session.setText(f"{equip_price *cur_time * discount:.2f}")
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
            self.parent().opened_form = False
        super().closeEvent(event)


class Halls(QMainWindow, set_hall_window.Ui_MainWindow):
    def __init__(self, id=None, name=None, placecount=None, update=False, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.id = id
        self.is_update = update
        self.equip_list = self.parent().equipment_list

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
        tmp = []
        for i in self.equip_list:
            if i['hall'] == self.id:
                tmp.append(int(i['place']))
        if self.name and self.placecount:
            try:
                if not self.is_update:
                    query = dbrequests.add_hall(self.name, str(self.placecount))
                    db.execute_query(query)
                    self.close()
                else:
                    if int(self.placecount) > max(tmp):
                        query = dbrequests.update_hall(self.id, self.name, str(self.placecount))
                        db.execute_query(query)
                        self.close()
                    else:
                        self.show_warning("У вас есть оборудование на позициях больше!")
            except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def del_hall(self):
        if self.name and self.placecount:
            flag = True
            for i in self.equip_list:
                if i['hall'] == self.id:
                    flag = False
                    self.show_warning('Этот зал не пуст')
                    break
            if flag:
                try:
                    query = dbrequests.del_hall(self.id)
                    db.execute_query(query)
                    self.close()
                except pymysql.Error:
                    self.show_warning('Ошибка отправки данных на сервер')
        else:
            self.show_warning("Присутствуют незаполненные поля!")

    def change_hallname(self, text):
        self.name = text.lstrip().rstrip()

    def change_placecount(self, text):
        self.placecount = text.lstrip().rstrip()

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


def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Предупреждение")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

def main():
    try:
        users = db.fetch_all(dbrequests.get_admin())
        users = db.decrypt_data(users)
        app = QApplication(sys.argv)
        window = Login(admins=users)
        window.show()
        app.exec()
    except pymysql.Error:
        show_warning('Ошибка получения данных')
    except Exception:
        show_warning('Ошибка!')
    finally:
        db.close()

if __name__ == "__main__":
    try:
        db = Database('150.241.90.210', 'justEt', dbpassword, 'justEtCursach', dbkey)
        main()
    except pymysql.Error:
        show_warning('Ошибка подключения к базе данных')

