import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui_py.ui_mainwindow import Ui_MainWindow
from ui_py.accounts.ui_loginform import Ui_LoginForm
from ui_py.accounts.ui_signupform import Ui_SignUpForm
from ui_py.ui_homedashboardform import Ui_HomeSpotifyForm

from model.accounts import Account, ListAccounts
    

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.showFullScreen()
        self.btnLogin.clicked.connect(self.showFormLogin)
        self.btnSignUp.clicked.connect(self.showFormSignUp)

    def showFormLogin(self):
        self.close()
        login.show()
    def showFormSignUp(self):
        self.close()
        signup.show()

class LoginForm(QMainWindow, Ui_LoginForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnLogin.clicked.connect(self.Login)
        self.accs = ListAccounts()
    def show(self):
        self.showFullScreen()
    def Login(self):
        us = self.txtUserName.text()
        pw = self.txtPassWord.text()
        AccountCheck = Account(us,pw)
        if self.accs.checkAccount(AccountCheck):
            home.show()
            self.close()
        else:
            return None   

class SignUpForm(QMainWindow, Ui_SignUpForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnRegister.clicked.connect(self.Register)
        self.accs = ListAccounts()
    def show(self):
        self.showFullScreen() 
    def Register(self):
        us = self.txtUserName.text()
        pw = self.txtPassWord.text()
        em = self.txtGmail.text()
        AccountCheck = Account(us,pw,em)
        if self.accs.addAccount(AccountCheck):
            print("Account added successfully")
            login.show()
            self.close()
        else:
            print("Account has already been")

class HomeSpotifyDashBoard(QMainWindow, Ui_HomeSpotifyForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    def show(self):
        self.showFullScreen() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    login = LoginForm()
    signup = SignUpForm()
    home = HomeSpotifyDashBoard()
    window.show()
    app.exec()
    
