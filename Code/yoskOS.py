import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QLineEdit, QToolBar
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl

SAVE_DIRECTORY = "Desktop klasörü(örnek : C:\Users\monster\Desktop\yoskOS\file)"

class DraggableButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent; border: none;")
        self.setFixedSize(100, 100)  # Fixed size for simplicity
        self.setIconSize(QtCore.QSize(48, 48))
        
        self.setAcceptDrops(True)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.pos()
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        
        if (event.pos() - self.drag_start_position).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(self.text())  # Set the text for drag
            drag.setMimeData(mime_data)
            drag.setHotSpot(self.rect().center())
            drag.exec_(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            # Handle the drop event
            self.move(event.pos() - self.rect().center())
            event.acceptProposedAction()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_files()

    def initUI(self):
        self.setWindowTitle('yoskOS')
        self.setGeometry(100, 100, 1000, 590)

        # Background image setup
        self.background_label = QtWidgets.QLabel(self)
        self.background_label.setGeometry(0, 0, 1000, 590)
        self.set_background_image()

        # Menu button setup
        self.icon = QtGui.QIcon("win.jpg")
        self.pixmap = self.icon.pixmap(QtCore.QSize(40, 40))
        self.menu_button = QtWidgets.QPushButton(self)
        self.menu_button.setGeometry(10, 540, self.pixmap.width(), self.pixmap.height())
        self.menu_button.setIcon(self.icon)
        self.menu_button.setIconSize(self.pixmap.size())
        self.menu_button.setStyleSheet("""
            border: none;
            border-radius: 10px;
            padding: 0;
            background: transparent;
        """)
        self.menu_button.clicked.connect(self.showMenu)

        # Menu setup
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Text Editor', self.open_text_editor)
        self.menu.addAction('Browser', self.open_browser)
        self.menu.addAction('App Store', self.open_store)


        # Taskbar setup
        self.taskbar = QtWidgets.QWidget(self)
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        self.taskbar_layout = QtWidgets.QHBoxLayout(self.taskbar)
        self.taskbar_layout.setContentsMargins(0, 0, 0, 0)
        self.taskbar_layout.setSpacing(0)

        # Add buttons to taskbar
        self.create_taskbar_button("Text Editor", "text.png", self.open_text_editor)
        self.create_taskbar_button("Browser", "browser_icon.png", self.open_browser)
        self.create_taskbar_button("App Store", "store_icon.png", self.open_store)

        # File icons layout setup
        self.files_widget = QtWidgets.QWidget(self)
        self.files_layout = QtWidgets.QGridLayout(self.files_widget)
        self.files_layout.setContentsMargins(10, 10, 10, 60)
        self.files_layout.setSpacing(10)
        self.files_layout.setAlignment(QtCore.Qt.AlignTop)
        self.files_widget.setLayout(self.files_layout)

        # Add the files_widget to the main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.files_widget)
        self.main_layout.addWidget(self.taskbar)

    def create_taskbar_button(self, text, icon_path, callback=None):
        button = QtWidgets.QPushButton(text, self.taskbar)
        button.setIcon(QtGui.QIcon(icon_path))
        
        # Set a larger icon size
        button.setIconSize(QtCore.QSize(64, 64))  # Adjust the size as needed

        button.setStyleSheet("""
            border: none;
            border-radius: 5px;
            padding: 5px;
            background: transparent;
        """)
        if callback:
            button.clicked.connect(callback)
        self.taskbar_layout.addWidget(button)


    def set_background_image(self):
        oImage = QtGui.QImage("bg_1.png")
        sImage = oImage.scaled(self.size(), QtCore.Qt.KeepAspectRatioByExpanding)
        palette = QtGui.QPalette()
        palette.setBrush(10, QtGui.QBrush(sImage))
        self.setPalette(palette)

    def showMenu(self):
        menu_position = self.menu_button.mapToGlobal(QtCore.QPoint(0, -self.menu.height()))
        self.menu.exec_(menu_position)


    def open_text_editor(self):
        self.text_editor = TextEditor(self)
        self.text_editor.show()

    def open_browser(self):
        self.browser_window = BrowserWindow(self)
        self.browser_window.show()

    def open_store(self):
        self.store_window = StoreWindow(self)
        self.store_window.show()

    def add_file_icon(self, file_path):
        file_name = file_path.split('/')[-1]
        file_ext = os.path.splitext(file_name)[1]
        
        # Choose the icon based on the file extension
        if file_ext == '.txt':
            icon_path = 'text.png'
        elif file_ext == '.py':
            icon_path = 'python.png'
        elif file_ext == '.exe':
            icon_path = 'exe.png'  # Use a specific icon for exe files
        else:
            icon_path = 'default.png'  # Use a default icon for other file types
        
        button = DraggableButton(file_name, self.files_widget)
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(48, 48))
        button.setStyleSheet("""
            border: none;
            border-radius: 5px;
            padding: 5px;
            background: transparent;
        """)
        
        if file_ext == '.exe':
            button.clicked.connect(lambda: self.execute_file(file_path))
        else:
            button.clicked.connect(lambda: self.open_file(file_path))
            
        self.files_layout.addWidget(button)

    def execute_file(self, file_path):
        subprocess.Popen(file_path, shell=True)

    def open_file(self, file_path):
        self.text_editor = TextEditor(self)
        self.text_editor.open_file(file_path)
        self.text_editor.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Meta:  # Windows tuşu
            self.showMenu()

    def resizeEvent(self, event):
        self.set_background_image()
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.menu_button.setGeometry(10, self.height() - self.pixmap.height() - 10, self.pixmap.width(), self.pixmap.height())
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)

    def load_files(self):
        if not os.path.exists(SAVE_DIRECTORY):
            os.makedirs(SAVE_DIRECTORY)
        for file_name in os.listdir(SAVE_DIRECTORY):
            if os.path.isfile(os.path.join(SAVE_DIRECTORY, file_name)):
                self.add_file_icon(os.path.join(SAVE_DIRECTORY, file_name))

class TextEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # TextEdit widget
        self.textEdit = QTextEdit(self)
        self.setCentralWidget(self.textEdit)
        
        # Create actions
        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)
        
        saveFile = QAction(QIcon('save.png'), 'Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.saveDialog)
        
        # Create menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Simple Text Editor')
        
    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/new')[0]
        
        if fname:
            with open(fname, 'r') as f:
                data = f.read()
                self.textEdit.setText(data)
                
    def saveDialog(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file', '/new')[0]
        
        if fname:
            with open(fname, 'w') as f:
                data = self.textEdit.toPlainText()
                f.write(data)
                
    def open_file(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()
            self.textEdit.setText(data)

class BrowserWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.browser = QWebEngineView()
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.on_download_requested)
        self.browser.setUrl(QUrl('https://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

        # Set window properties
        self.setGeometry(300, 300, 1200, 800)
        self.setWindowTitle('Web Browser')

    def navigate_home(self):
        self.browser.setUrl(QUrl('https://google.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def on_download_requested(self, download):
        download.setPath(os.path.join(SAVE_DIRECTORY, download.suggestedFileName()))
        download.accept()

class StoreWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.browser = QWebEngineView()
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.on_download_requested)
        self.browser.setUrl(QUrl.fromLocalFile(os.path.join(SAVE_DIRECTORY, 'appstore.html')))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

        # Set window properties
        self.setGeometry(300, 300, 1200, 800)
        self.setWindowTitle('App Store')

    def navigate_home(self):
        self.browser.setUrl(QUrl.fromLocalFile(os.path.join(SAVE_DIRECTORY, 'appstore.html')))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def on_download_requested(self, download):
        download.setPath(os.path.join(SAVE_DIRECTORY, download.suggestedFileName()))
        download.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
