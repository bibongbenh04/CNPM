# ################### Optimizing imports for all files #########################
# ################### All imports are fetched from here ########################
################################################################################

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QAbstractListModel, QUrl, Signal, QThread, QObject, Slot
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import QApplication, QMainWindow,\
    QVBoxLayout, QListView, QWidget, QFileDialog
from PySide6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import QTimer
from mutagen.mp3 import MP3
from pygame import mixer
import ntpath
import pygame
import time
import os
import sys
from pathlib import Path
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from ui_py.ui_mainwindow import Ui_MainWindow
from ui_py.accounts.ui_loginform import Ui_LoginForm
from ui_py.accounts.ui_signupform import Ui_SignUpForm
from ui_py.ui_homedashboardform import Ui_HomeSpotifyForm
# import sqlite3

# from src.playlist import PlayLists
# from widgets.play_button import PlayButton
# from src.widget_callback import *
# from src.audio_callback import play_next, play_previous
# from src.ui_update import Runner, default_status_size, hide_sideBar, reset_status, load_progress, reset_progress