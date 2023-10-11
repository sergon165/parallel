from typing import Optional, Callable, List, Tuple

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel

from actions import Action
from settings import Settings
from timetable import Timetable
from views.action_widget import ActionWidget


class ActionInTableWidget(QWidget):
    def __init__(self, clock: int, executor: int, settings: Settings, timetable: Timetable,
                 update_table: Callable[..., None]):
        super().__init__()
        uic.loadUi('views/ui/actionInTable.ui', self)

        self._clock = clock
        self._executor = executor
        self._settings = settings
        self._timetable = timetable
        self._update_table = update_table
        self._action_widget: Optional[ActionWidget] = None

        self.render_action(None)

        self.setAcceptDrops(True)

    def render_action(self, action: Optional[Action]):
        if action is None:
            self.findChild(QLabel, 'taskLabel').hide()
            self.findChild(QLabel, 'executorLabel').hide()
            self.findChild(QLabel, 'afterLabel').hide()
            self.findChild(QLabel, 'usedResourcesLabel').hide()
            self.findChild(QLabel, 'newResourcesLabel').hide()
            self.findChild(QLabel, 'durationLabel').hide()
            return

        task_label: QLabel = self.findChild(QLabel, 'taskLabel')
        task_label.setText(action.get_name())
        task_label.show()

        executor_label: QLabel = self.findChild(QLabel, 'executorLabel')
        if self._settings.specific_executors_enabled:
            executor_label.setText(str(action.executor_list))
            executor_label.show()
        else:
            executor_label.hide()

        after_label: QLabel = self.findChild(QLabel, 'afterLabel')
        if len(action.previous_action_list) > 0:
            after_label.setText('После: ' + str(action.previous_action_list))
            after_label.show()
        else:
            after_label.hide()

        used_resources_label: QLabel = self.findChild(QLabel, 'usedResourcesLabel')
        if self._settings.resources_enabled and len(action.required_resource_list) > 0:
            used_resources_label.setText('- ' + str(action.required_resource_list))
            used_resources_label.show()
        else:
            used_resources_label.hide()

        new_resources_label: QLabel = self.findChild(QLabel, 'newResourcesLabel')
        if self._settings.resources_enabled and len(action.result_resource_list) > 0:
            new_resources_label.setText('+ ' + str(action.result_resource_list))
            new_resources_label.show()
        else:
            new_resources_label.hide()

        duration_label: QLabel = self.findChild(QLabel, 'durationLabel')
        duration_label.setText(action.get_duration_str())
        duration_label.show()

    def is_empty(self) -> bool:
        return self._action_widget is None

    def get_position(self) -> Tuple[int, int]:
        return self._clock, self._executor

    def get_duration(self) -> int:
        return self._action_widget.action.get_duration()

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        e.accept()
        action_widget: ActionWidget = e.source()
        action_widget.hide()
        self._action_widget = action_widget

        action = action_widget.action
        self._timetable.add_action(action, self._clock, self._executor)
        self.render_action(action)
        self._update_table(self, action)

        self._timetable.print_timetable()

    def mousePressEvent(self, e):
        if e.buttons() == Qt.MouseButton.RightButton and self._action_widget is not None:
            action = self._action_widget.action
            self._timetable.remove_action(action)

            self._action_widget.show()
            self._action_widget = None
            self.render_action(None)

            self._update_table(self, action)

        self._timetable.print_timetable()
