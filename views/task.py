from typing import Optional, List

from PyQt6 import uic
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy, QGridLayout, \
    QPushButton, QMessageBox

from actions import Action
from tasks import Task
from timetable import Timetable
from views.action_in_table_widget import ActionInTableWidget
from views.action_widget import ActionWidget


class TaskWindow(QMainWindow):
    def __init__(self, task: Task, src: str, size: Optional[QSize] = None, pos: Optional[QPoint] = None):
        super().__init__()
        uic.loadUi('views/ui/task.ui', self)

        self._task = task
        self._clock_count = 0
        self._open_menu = True

        self._timetable = Timetable(task)

        self._src = src
        self.setWindowTitle(self.windowTitle() + f' - {src}')

        self.set_menubar()
        self.set_task(task)
        self.add_clock()

        self.findChild(QPushButton, 'checkBtn').clicked.connect(self.check)

        if size:
            self.resize(size)
        if pos:
            self.move(pos)

    def set_menubar(self):
        constructor_mode: QAction = self.findChild(QAction, 'constructorModeAction')
        constructor_mode.triggered.connect(self.enter_constructor_mode)

    def enter_constructor_mode(self):
        from views.constructor import ConstructorWindow
        self._open_menu = False
        self._constructor_window = ConstructorWindow(self._task, self._src, self.size(), self.pos())
        self.close()
        self._constructor_window.show()

    def set_task(self, task: Task):
        # Устанавливаем описание задания
        self.findChild(QLabel, 'taskDescLabel').setText(task.get_description())

        # Устанавливаем список ресурсов
        self.findChild(QLabel, 'resourcesListLabel').setText(str(task.resource_list) + '.')

        # Устанавливаем список действий
        action_container: QWidget = self.findChild(QWidget, 'actionScrollAreaWidgetContents')
        layout = action_container.layout()
        for action in task.action_list:
            action_widget = ActionWidget(action, task.settings)
            layout.addWidget(action_widget)
        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Устанавливаем таблицу расписания
        timetable_widget: QWidget = self.findChild(QWidget, 'timetableContentWidget')
        timetable_layout: QGridLayout = timetable_widget.layout()
        number = 1
        for (executor, count) in task.executor_list:
            for i in range(count):
                executor_widget = QWidget()
                layout = QVBoxLayout(executor_widget)
                layout.setSpacing(0)

                number_label = QLabel(str(number))
                number_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(number_label)

                executor_label = QLabel(executor.get_name())
                executor_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(executor_label)

                timetable_layout.addWidget(executor_widget, 0, number)
                number += 1

    def add_clock(self, count: int = 1):
        timetable_widget: QWidget = self.findChild(QWidget, 'timetableContentWidget')
        timetable_layout: QGridLayout = timetable_widget.layout()

        for i in range(count):
            self._clock_count += 1
            clock_label = QLabel(str(self._clock_count))
            clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            timetable_layout.addWidget(clock_label, self._clock_count, 0)

            for j in range(self._task.get_executor_count()):
                action_widget: QWidget = ActionInTableWidget(self._clock_count, j + 1, self._task.settings,
                                                             self._timetable, self._update_table)
                timetable_layout.addWidget(action_widget, self._clock_count, j + 1)

    def remove_last_clock(self, count: int = 1):
        timetable_widget: QWidget = self.findChild(QWidget, 'timetableContentWidget')
        timetable_layout: QGridLayout = timetable_widget.layout()

        for i in range(count):
            for col in range(timetable_layout.columnCount()):
                item = timetable_layout.itemAtPosition(self._clock_count, col)
                widget = item.widget()
                widget.deleteLater()
                timetable_layout.removeItem(item)
            self._clock_count -= 1

    def _update_table(self, widget: ActionInTableWidget, action: Action):
        timetable_widget: QWidget = self.findChild(QWidget, 'timetableContentWidget')
        timetable_layout: QGridLayout = timetable_widget.layout()
        row, col = widget.get_position()
        duration = action.get_duration()
        diff = self._timetable.get_clock_count() - self._clock_count

        if diff > 0:
            self.add_clock(diff)

        if widget.is_empty():
            timetable_layout.removeWidget(widget)
            timetable_layout.addWidget(widget, row, col)
            for i in range(1, duration):
                action_widget: QWidget = ActionInTableWidget(row + i, col, self._task.settings,
                                                             self._timetable, self._update_table)
                timetable_layout.addWidget(action_widget, row + i, col)
        else:
            timetable_layout.removeWidget(widget)
            for i in range(1, duration):
                item = timetable_layout.itemAtPosition(row + i, col)
                if item:
                    item.widget().deleteLater()
                    timetable_layout.removeItem(item)
            timetable_layout.addWidget(widget, row, col, duration, 1)

        if diff < 0:
            self.remove_last_clock(-diff)

    def check(self):
        mistakes = self._timetable.check()
        dlg = QMessageBox(self)
        if len(mistakes) == 0:
            dlg.setText('Ошибок нет!')
        else:
            text = ''
            for mistake in mistakes:
                text += f'- {mistake}\n'
            dlg.setText(text)
        dlg.exec()

    def closeEvent(self, e):
        from views.menu import MenuWindow
        self._menu_window = MenuWindow()
        if self._open_menu:
            self._menu_window.show()
        e.accept()
