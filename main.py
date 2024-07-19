from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6 import uic
import sys


class SpotifyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(SpotifyApp, self).__init__()
        uic.loadUi('yourfile.ui', self)

        # Kết nối đến Spotify API
        

app = QtWidgets.QApplication(sys.argv)
window = SpotifyApp()
window.show()
sys.exit(app.exec_())














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