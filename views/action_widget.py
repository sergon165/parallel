from typing import Optional, Callable

from PyQt6 import uic
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton

from actions import Action
from settings import Settings
from tasks import Task
from views.action_dialog import ActionDialog


class ActionWidget(QWidget):
    def __init__(self, action: Action, settings: Settings, set_changed: Optional[Callable[[], None]] = None,
                 show_buttons: bool = False, task: Optional[Task] = None,
                 set_task=None):
        super().__init__()
        uic.loadUi('views/ui/action.ui', self)

        self.action = action
        self._settings = settings
        self._set_changed = set_changed
        self._task = task
        self.render_action()

        layout = self.layout()
        layout.setContentsMargins(0, 0, 0, 0)

        if not show_buttons:
            buttons_widget: QWidget = self.findChild(QWidget, 'buttonsWidget')
            buttons_widget.hide()
        else:
            self.editBtn: QPushButton
            self.editBtn.clicked.connect(self.edit)
            self.deleteBtn: QPushButton
            self.deleteBtn.clicked.connect(self.remove)

        # print(action.previous_action_list)

    def render_action(self):
        action = self.action
        settings = self._settings

        self.findChild(QLabel, 'taskLabel').setText(action.get_name())
        self.findChild(QLabel, 'durationLabel').setText(action.get_duration_str())

        executor_label: QLabel = self.findChild(QLabel, 'executorLabel')
        if settings.specific_executors_enabled:
            executor_label.show()
            executor_label.setText(str(action.executor_list))
        else:
            executor_label.hide()

        after_label: QLabel = self.findChild(QLabel, 'afterLabel')
        if len(action.previous_action_list) > 0:
            after_label.show()
            after_label.setText('После: ' + str(action.previous_action_list))
        else:
            after_label.hide()

        resources_label: QLabel = self.findChild(QLabel, 'resourcesLabel')
        if settings.resources_enabled:
            res = ''
            if len(action.required_resource_list) > 0:
                res += str(action.required_resource_list)
            else:
                res += '-'
            if len(action.result_resource_list) > 0:
                res += ' -> ' + str(action.result_resource_list)
            resources_label.setText(res)
            resources_label.show()
        else:
            resources_label.hide()

        # print(action.previous_action_list)

    def edit(self):
        action_dialog = ActionDialog(self._task, self._set_changed, self.action)
        action_dialog.exec()
        self.render_action()

    def remove(self):
        self._set_changed()
        self._task.action_list.remove(self.action)
        self.deleteLater()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec()
