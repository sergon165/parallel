from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QPushButton

from file_manager import FileManager
from views.constructor import ConstructorWindow
from views.task import TaskWindow


class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('views/ui/menu.ui', self)
        self.findChild(QPushButton, 'openBtn').clicked.connect(self.open)
        self.findChild(QPushButton, 'constructorBtn').clicked.connect(self.constructor)
        self.findChild(QPushButton, 'exitBtn').clicked.connect(self.exit)

    def constructor(self):
        self.constructor_window = ConstructorWindow()
        self.close()
        self.constructor_window.show()

    def open(self):
        src, _ = QFileDialog.getOpenFileName()
        task = FileManager.load(src)
        self.task_window = TaskWindow(task, src)
        self.close()
        self.task_window.show()

    def exit(self):
        self.close()
