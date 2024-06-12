import interface
from PyQt5 import QtWidgets, QtCore
import requests
from datetime import datetime
import reglog

USER = ""


class Registration(QtWidgets.QMainWindow, reglog.Ui_MainWindow):
    def __init__(self):
        super(Registration, self).__init__()
        self.setupUi(self)

        self.label.setText("")
        self.label_2.setText("Registration")
        self.lineEdit.setPlaceholderText("Enter a nickname")
        self.lineEdit_2.setPlaceholderText("Enter your password")
        self.pushButton.setText("Registration")
        self.pushButton_2.setText("Login")
        self.setWindowTitle("Registration")

        self.pushButton.clicked.connect(self.reg)
        self.pushButton_2.clicked.connect(self.open_login)

    def open_login(self):
        self.login = Login()
        self.login.show()
        self.hide()

    def reg(self):
        user_nickname = self.lineEdit.text()
        user_password = self.lineEdit_2.text()

        if user_nickname == "":
            self.label.setText("Enter the correct login!")
            return

        if user_password == "":
            self.label.setText("Enter the correct password!")
            return

        if len(user_nickname) > 3:
            try:
                response = requests.post(
                    url='http://127.0.0.1:5000/registration',
                    json={
                        'nickname': user_nickname,
                        'password': user_password
                    }
                )
            except Exception as e:
                print("The server is unavailable", e)
                return

            if response.status_code != 200:
                if response.json().get('error') == 'Nickname already taken':
                    self.label.setText("The nickname already taken")
                else:
                    self.label.setText("Registration error!")
                return

            self.label.setText(f"Account {user_nickname} successfully registered!")

            global USER
            USER = user_nickname
        else:
            self.label.setText("Nickname must consist of at least 4 characters!")
            return

        self.open_messenger()
        return

    def open_messenger(self):
        self.messenger = Messenger()
        self.messenger.show()
        self.hide()

class Login(QtWidgets.QMainWindow, reglog.Ui_MainWindow):
    def __init__(self):
        super(Login, self).__init__()
        self.setupUi(self)

        self.label.setText("")
        self.label_2.setText("Login")
        self.lineEdit.setPlaceholderText("Enter a nickname")
        self.lineEdit_2.setPlaceholderText("Enter your password")
        self.pushButton.setText("Login")
        self.pushButton_2.setText("Registration")
        self.setWindowTitle("Login")

        self.pushButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.open_reg)

    def open_reg(self):
        self.reg = Registration()
        self.reg.show()
        self.hide()

    def login(self):
        user_nickname = self.lineEdit.text()
        user_password = self.lineEdit_2.text()

        if user_nickname == '':
            self.label.setText("Enter the correct login")
            return

        if user_password == '':
            self.label.setText("Enter the correct password")
            return

        if len(user_nickname) > 0:
            try:
                response = requests.post(
                    url='http://127.0.0.1:5000/login',
                    json={
                        'nickname': user_nickname,
                        'password': user_password
                    }
                )
            except Exception:
                print("Server is not available")
                return

            if response.status_code != 200:
                self.label.setText('Authorisation Error')
                return

            global USER

            USER = user_nickname
            self.open_messenger()
            return

    def open_messenger(self):
        self.messenger = Messenger()
        self.messenger.show()
        self.hide()

class Messenger(QtWidgets.QMainWindow, interface.Ui_MainWindow):
    def __init__(self):
        super(Messenger, self).__init__()
        self.setupUi(self)
        self.after = 0
        self.pushButton.clicked.connect(self.send_message)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.get_messages)
        self.timer.start(1000)

    def show_messages(self, message):
        item = QtWidgets.QListWidgetItem()
        dt = datetime.fromtimestamp(message['time'])
        if message['name'] == USER:
            item.setTextAlignment(QtCore.Qt.AlignRight)
        item.setText(f"{message['name']} {dt.strftime('%H:%M')}\n{message['text']}")
        self.listWidget.addItem(item)

    def get_messages(self):
        try:
            response = requests.get(url='http://127.0.0.1:5000/messages', params={'after': self.after})
        except Exception as e:
            print(e)
            return
        messages = response.json()['messages']
        for i in range(len(messages)):
            self.show_messages(messages[i])
            self.after = messages[i]['time']
            self.listWidget.scrollToBottom()

    def send_message(self):
        global USER
        name = USER
        text = self.textEdit.toPlainText()
        if len(name) > 0 and len(text) > 0:
            try:
                response = requests.post(url='http://127.0.0.1:5000/send', json={'name': name, 'text': text})
            except Exception as e:
                item = QtWidgets.QListWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setText('Server is not available!\n')
                self.listWidget.addItem(item)
                print(e)
                return

            if response.status_code != 200:
                item = QtWidgets.QListWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setText('Wrong name or text!\n')
                self.listWidget.addItem(item)
                return

            self.textEdit.clear()


if __name__ == '__main__':
    App = QtWidgets.QApplication([])
    window = Login()
    window.show()
    App.exec()
