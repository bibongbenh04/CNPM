from imports import *

from model.accounts import Account, ListAccounts
from model.songs import Song, ListSong
from mutagen.mp3 import MP3
    

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.showFullScreen()
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
        self.l = ListSong()
        self.callAfterInit()
        pygame.mixer.init()
        self.current_volume = 0.5
        self.mixer = pygame.mixer.music
        self.mixer.set_volume(self.current_volume)
        self.btnAddSongs.clicked.connect(self.addSongs)
        self.btnPause.clicked.connect(self.pause)
        self.btnStop.clicked.connect(self.stop)
        self.diVolume.setValue(50)
        self.diVolume.valueChanged[int].connect(self.volumeChanged)
        self.Pause = False
        self.Stop = False
        self.song = None
        self.sldSong.sliderMoved[int].connect(self.on_slider_moved)
        self.timer = QTimer(self) 
        self.timer.timeout.connect(self.moveSlider)
    def moveSlider(self):
        if self.Stop:
            return
        else:
            if self.mixer.get_busy():
                self.sldSong.setMinimum(0)
                self.sldSong.setMaximum(int(self.song.info.length*1000))
                self.sldSong.setSingleStep(1000)
                self.updateSlider()
    def updateSlider(self):
        if self.mixer.get_busy():
            pos = self.mixer.get_pos()  # get_pos() returns milliseconds
            self.sldSong.setValue(pos)
        else:
            self.timer.stop()
        print(pos)
    def on_slider_moved(self):
        self.timer.stop()
        try:
            s = self.sldSong.value()
            self.mixer.set_pos(s//1000)
            print(self.mixer.get_pos())
        except Exception as e:
            print(e)
        self.timer.start()
    def volumeChanged(self):
        try:
            self.current_volume = self.diVolume.value()/100
            self.mixer.set_volume(self.current_volume)
            self.txtVolume.setText(str(int(self.current_volume*100)))
        except Exception as e:
            print("Volume change failed", e)
    def stop(self):
        try:
            self.mixer.stop()
            self.stop = True
            self.sldSong.setValue(0)
        except pygame.error as  e:
            print(e)
    def pause(self):
        if not self.Pause:
            try:
                self.mixer.pause()
            except pygame.error as e:
                return
        else:
            try:
                self.mixer.unpause()
            except pygame.error as e:
                return
        self.Pause = not self.Pause
    def callAfterInit(self):
        song_id = 1
        while self.gridLayout.count():
            child = self.gridLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for song in self.l.getAllSongs():
            songBut = QPushButton(parent=self.listSongs)
            songBut.setObjectName(str(id))
            songBut.setText(song.show())
            songBut.clicked.connect(lambda checked, s=song:self.playSong(s))
            self.gridLayout.addWidget(songBut)
            song_id +=1
        # self.listSongs.addItems(s.show() for s in self.l.getAllSongs())
    def playSong(self,song):
        try:
            self.Stop = False
            self.mixer.load(song.getUrl())
            self.song = MP3(song.getUrl())
            self.mixer.play(loops=0)
            self.timer.start(1000)
        except Exception as e:
            print(e)
    def addSongs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption="Add Songs to the app", directory=':\\',
            filter='Supported Files(*.mp3;*.mpeg;*.ogg;*.MP3;*.m4a;*.wma;*.acc;*.amr)'
        )
        if files:
            valid_extensions = ('.mp3', '.mpeg', '.ogg', '.m4a', '.wma', '.acc', '.amr')
            songs_dir = os.path.join(os.getcwd(), 'songs')

            if not os.path.exists(songs_dir):
                os.makedirs(songs_dir)

            for file in files:
                if file.lower().endswith(valid_extensions):
                    file_name = os.path.basename(file)
                    target_path = os.path.join(songs_dir, file_name)

                    # Ensure the file does not already exist in the target directory
                    if not os.path.exists(target_path):
                        newSong = Song(str(file_name),'Unknown','Unknown','Unknown',"songs/"+str(file_name))
                        listSong.add_song(newSong)
                        with open(file, 'rb') as src_file:
                            with open(target_path, 'wb') as dest_file:
                                dest_file.write(src_file.read())
                    else:
                        return None
                        # QMessageBox.warning(self, "File Exists", f"The file {file_name} already exists in the target directory.")
            print("Valid files added:", files)
            self.callAfterInit()

    def show(self):
        self.showFullScreen()

n = Song("123", "123", "123", "123", "D:/BiBongBenh/Downloads/Nhạc nền vui của Độ mixi.mp3")
if __name__ == "__main__":
    # n.play_song()
    listSong = ListSong()
    app = QApplication(sys.argv)
    pygame.init()
    window = MainWindow()
    login = LoginForm()
    signup = SignUpForm()
    home = HomeSpotifyDashBoard()
    # window.show()
    home.show()
    app.exec()