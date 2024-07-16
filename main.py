from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6 import uic
import sys

class LoginView(QMainWindow):
    def __init__(self) :
        super().__init__()
        uic.loadUi("./ui/welcome.ui", self)

class LoginView(QMainWindow):
    def __init__(self) :
        super().__init__()
        uic.loadUi("./ui/welcome.ui", self)
        
import pygame 
pygame. init()
my_sound = pygame. mixer. Sound('D:/BiBongBenh/Downloads/Nhạc nền vui của Độ mixi.mp3')



if __name__ == "__main__":
    # my_sound.play()
    app = QApplication(sys.argv)
    login = LoginView()
    login.show()
    app.exec()














# from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
# from PyQt6 import uic
# import sys

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         uic.loadUi("ui/main_window.ui", self)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())