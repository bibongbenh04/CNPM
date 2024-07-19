# Form implementation generated from reading ui file 'ui/home.ui'
#
# Created by: PyQt6 UI code generator 6.7.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_HomeSpotifyForm(object):
    def setupUi(self, HomeSpotifyForm):
        HomeSpotifyForm.setObjectName("HomeSpotifyForm")
        HomeSpotifyForm.resize(1500, 1000)
        HomeSpotifyForm.setMinimumSize(QtCore.QSize(0, 0))
        HomeSpotifyForm.setStyleSheet("#FormWelcome {\n"
"    background:url(D:/BiBongBenh/Desktop/CNPM/img/spotify-home.png);\n"
"}")
        self.FormWelcome = QtWidgets.QWidget(parent=HomeSpotifyForm)
        self.FormWelcome.setStyleSheet("#FormWelcome {\n"
"    back-ground:url(D:/BiBongBenh/Desktop/CNPM/img/login.png);\n"
"}")
        self.FormWelcome.setObjectName("FormWelcome")
        self.listSongs = QtWidgets.QWidget(parent=self.FormWelcome)
        self.listSongs.setGeometry(QtCore.QRect(550, 380, 841, 400))
        self.listSongs.setMinimumSize(QtCore.QSize(841, 400))
        self.listSongs.setObjectName("listSongs")
        self.gridLayout = QtWidgets.QGridLayout(self.listSongs)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.btnAddSongs = QtWidgets.QPushButton(parent=self.FormWelcome)
        self.btnAddSongs.setGeometry(QtCore.QRect(560, 290, 93, 28))
        self.btnAddSongs.setObjectName("btnAddSongs")
        self.btnPause = QtWidgets.QPushButton(parent=self.FormWelcome)
        self.btnPause.setGeometry(QtCore.QRect(670, 290, 93, 28))
        self.btnPause.setObjectName("btnPause")
        self.btnStop = QtWidgets.QPushButton(parent=self.FormWelcome)
        self.btnStop.setGeometry(QtCore.QRect(790, 290, 93, 28))
        self.btnStop.setObjectName("btnStop")
        self.diVolume = QtWidgets.QDial(parent=self.FormWelcome)
        self.diVolume.setGeometry(QtCore.QRect(920, 80, 181, 181))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.diVolume.setFont(font)
        self.diVolume.setMouseTracking(False)
        self.diVolume.setTabletTracking(False)
        self.diVolume.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.PreventContextMenu)
        self.diVolume.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
        self.diVolume.setMaximum(100)
        self.diVolume.setWrapping(False)
        self.diVolume.setNotchesVisible(True)
        self.diVolume.setObjectName("diVolume")
        self.txtVolume = QtWidgets.QLabel(parent=self.FormWelcome)
        self.txtVolume.setGeometry(QtCore.QRect(960, 130, 101, 81))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.txtVolume.setFont(font)
        self.txtVolume.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtVolume.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.txtVolume.setScaledContents(False)
        self.txtVolume.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtVolume.setObjectName("txtVolume")
        self.sldSong = QtWidgets.QSlider(parent=self.FormWelcome)
        self.sldSong.setGeometry(QtCore.QRect(560, 810, 791, 31))
        self.sldSong.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.sldSong.setObjectName("sldSong")
        HomeSpotifyForm.setCentralWidget(self.FormWelcome)

        self.retranslateUi(HomeSpotifyForm)
        QtCore.QMetaObject.connectSlotsByName(HomeSpotifyForm)

    def retranslateUi(self, HomeSpotifyForm):
        _translate = QtCore.QCoreApplication.translate
        HomeSpotifyForm.setWindowTitle(_translate("HomeSpotifyForm", "MainWindow"))
        self.btnAddSongs.setText(_translate("HomeSpotifyForm", "Add Songs"))
        self.btnPause.setText(_translate("HomeSpotifyForm", "Pause"))
        self.btnStop.setText(_translate("HomeSpotifyForm", "Stop"))
        self.txtVolume.setText(_translate("HomeSpotifyForm", "50"))