from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QDialog, QComboBox, QLineEdit, QSpinBox, QListView, QTableView

from actions import Action
from tasks import Task


class ActionDialog(QDialog):
    def __init__(self, task: Task, action: Optional[Action] = Action()):
        super().__init__()
        uic.loadUi('views/ui/addAction.ui', self)

        self._task = task
        self._action = action

        self.nameLineEdit: QLineEdit
        self.nameLineEdit.setText(action.get_name())

        self.durationSpinBox: QSpinBox
        self.durationSpinBox.setValue(action.get_duration())

        # Устанавливаем список исполнителей
        self.executorsComboBox: QComboBox
        for executor, _ in task.executor_list:
            self.executorsComboBox.addItem(str(executor), executor)

        self.executorsListView: QListView
        executors_model = QStandardItemModel()
        self.executorsListView.setModel(executors_model)
        for executor, _ in action.executor_list:
            item = QStandardItem()
            item.setData(executor.get_name(), Qt.ItemDataRole.DisplayRole)
            item.setData(executor, Qt.ItemDataRole.UserRole)
            executors_model.appendRow(item)

        # Устанавливаем список ресурсов
        self.resourcesComboBox: QComboBox
        for resource, _ in task.resource_list:
            self.resourcesComboBox.addItem(str(resource), resource)

        # - Используемые ресурсы
        self.usedResourcesTableView: QTableView
        used_resources_model = QStandardItemModel()
        self.usedResourcesTableView.setModel(used_resources_model)
        used_resources_model.setHorizontalHeaderLabels(['Ресурс', 'Количество'])
        for resource, count in action.required_resource_list:
            name = QStandardItem(str(resource))
            c = QStandardItem()
            c.setData(count, Qt.ItemDataRole.DisplayRole)
            used_resources_model.appendRow([name, c])

        # - Получаемые ресурсы
        self.newResourcesTableView: QTableView
        new_resources_model = QStandardItemModel()
        self.newResourcesTableView.setModel(new_resources_model)
        new_resources_model.setHorizontalHeaderLabels(['Ресурс', 'Количество'])
        for resource, count in action.result_resource_list:
            name = QStandardItem(str(resource))
            c = QStandardItem()
            c.setData(count, Qt.ItemDataRole.DisplayRole)
            new_resources_model.appendRow([name, c])

        # Устанавливаем список ограничений
        self.afterComboBox: QComboBox
        for action in task.action_list:
            self.afterComboBox.addItem(str(action), action)

        self.afterListView: QListView
        after_model = QStandardItemModel()
        self.afterListView.setModel(after_model)
        for action in action.previous_action_list:
            item = QStandardItem()
            item.setData(action.get_name(), Qt.ItemDataRole.DisplayRole)
            item.setData(action, Qt.ItemDataRole.UserRole)
            after_model.appendRow(item)
