from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton

from actions import Action
from settings import Settings
from tasks import Task
from views.action_dialog import ActionDialog


class ActionWidget(QWidget):
    def __init__(self, action: Action, settings: Settings, show_buttons: bool = False, task: Optional[Task] = None):
        super().__init__()
        uic.loadUi('views/ui/action.ui', self)

        self.action = action
        self._settings = settings
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

    def render_action(self):
        action = self.action
        settings = self._settings

        self.findChild(QLabel, 'taskLabel').setText(action.get_name())
        self.findChild(QLabel, 'durationLabel').setText(action.get_duration_str())

        executor_label: QLabel = self.findChild(QLabel, 'executorLabel')
        if settings.specific_executors_enabled:
            executor_label.setText(str(action.executor_list))
        else:
            executor_label.hide()
            executor_label.deleteLater()

        after_label: QLabel = self.findChild(QLabel, 'afterLabel')
        if len(action.previous_action_list) > 0:
            after_label.setText('После: ' + str(action.previous_action_list))
        else:
            after_label.hide()
            after_label.deleteLater()

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
        else:
            resources_label.hide()
            resources_label.deleteLater()

    def edit(self):
        action_dialog = ActionDialog(self._task, self.action)
        action_dialog.exec()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec()
