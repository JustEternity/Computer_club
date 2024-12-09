# Form implementation generated from reading ui file 'login-window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(230, 210)
        MainWindow.setMinimumSize(QtCore.QSize(230, 210))
        MainWindow.setMaximumSize(QtCore.QSize(230, 210))
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.centralwidget.setStyleSheet("#centralwidget{\n"
"background-color: #131936;\n"
"}")
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 13, 211, 191))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.password_label = QtWidgets.QLabel(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.password_label.sizePolicy().hasHeightForWidth())
        self.password_label.setSizePolicy(sizePolicy)
        self.password_label.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight SemiConde")
        font.setPointSize(14)
        self.password_label.setFont(font)
        self.password_label.setStyleSheet("#password_label{\n"
"color: white;\n"
"}")
        self.password_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.password_label.setObjectName("password_label")
        self.gridLayout.addWidget(self.password_label, 2, 0, 1, 1)
        self.login_label = QtWidgets.QLabel(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.login_label.sizePolicy().hasHeightForWidth())
        self.login_label.setSizePolicy(sizePolicy)
        self.login_label.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight SemiConde")
        font.setPointSize(14)
        self.login_label.setFont(font)
        self.login_label.setStyleSheet("#login_label{\n"
"color: white;\n"
"}")
        self.login_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.login_label.setObjectName("login_label")
        self.gridLayout.addWidget(self.login_label, 0, 0, 1, 1)
        self.edit_login = QtWidgets.QLineEdit(parent=self.layoutWidget)
        self.edit_login.setMinimumSize(QtCore.QSize(0, 30))
        self.edit_login.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight SemiConde")
        font.setPointSize(14)
        self.edit_login.setFont(font)
        self.edit_login.setStyleSheet("#edit_login{\n"
"    background-color: transparent;\n"
"    border: 1px solid gray;\n"
"    color: white;\n"
"}")
        self.edit_login.setMaxLength(100)
        self.edit_login.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.edit_login.setObjectName("edit_login")
        self.gridLayout.addWidget(self.edit_login, 1, 0, 1, 1)
        self.edit_password = QtWidgets.QLineEdit(parent=self.layoutWidget)
        self.edit_password.setMinimumSize(QtCore.QSize(0, 30))
        self.edit_password.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight SemiConde")
        font.setPointSize(14)
        self.edit_password.setFont(font)
        self.edit_password.setStyleSheet("#edit_password{\n"
"    background-color: transparent;\n"
"    border: 1px solid gray;\n"
"    color: white;\n"
"}")
        self.edit_password.setMaxLength(30)
        self.edit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.edit_password.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.edit_password.setObjectName("edit_password")
        self.gridLayout.addWidget(self.edit_password, 3, 0, 1, 1)
        self.login_button = QtWidgets.QPushButton(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.login_button.sizePolicy().hasHeightForWidth())
        self.login_button.setSizePolicy(sizePolicy)
        self.login_button.setMinimumSize(QtCore.QSize(100, 35))
        self.login_button.setMaximumSize(QtCore.QSize(10000, 35))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight SemiConde")
        font.setPointSize(14)
        self.login_button.setFont(font)
        self.login_button.setStyleSheet("#login_button{\n"
"    background-color: rgb(92, 17, 255);\n"
"color: white;\n"
"}")
        self.login_button.setCheckable(False)
        self.login_button.setObjectName("login_button")
        self.gridLayout.addWidget(self.login_button, 4, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Компьютерный клуб"))
        self.password_label.setText(_translate("MainWindow", "Пароль"))
        self.login_label.setText(_translate("MainWindow", "Логин"))
        self.login_button.setText(_translate("MainWindow", "Вход"))