from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QPushButton, QMessageBox

from file_manager import FileManager
from views.constructor import ConstructorWindow
from views.task import TaskWindow


class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('views/ui/menu.ui', self)
        self.findChild(QPushButton, 'openBtn').clicked.connect(self.open)
        self.findChild(QPushButton, 'constructorBtn').clicked.connect(self.constructor)
        self.findChild(QPushButton, 'aboutBtn').clicked.connect(self.about)
        self.findChild(QPushButton, 'exitBtn').clicked.connect(self.exit)

    def constructor(self):
        self.constructor_window = ConstructorWindow()
        self.close()
        self.constructor_window.show()

    def open(self):
        src, _ = QFileDialog.getOpenFileName()
        if src == '':
            return
        task = FileManager.load(src)
        if task is None:
            dlg = QMessageBox()
            dlg.setText('Ошибка чтения файла')
            dlg.exec()
            return
        self.task_window = TaskWindow(task, src)
        self.close()
        self.task_window.show()

    def about(self):
        dlg = QMessageBox()
        dlg.setText('Программа разработана в рамках курсовой работы за 3 курс Гончаровым С.А.')
        dlg.exec()

    def exit(self):
        self.close()
