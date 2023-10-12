from typing import Optional

from PyQt6 import uic
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QDialog, QComboBox, QLineEdit, QSpinBox, QListView, QTableView, QPushButton, \
    QMessageBox

from actions import Action
from resources import Resource
from tasks import Task


class ActionDialog(QDialog):
    nameLineEdit: QLineEdit

    executorsComboBox: QComboBox
    afterComboBox: QComboBox
    resourcesComboBox: QComboBox

    executorsListView: QListView
    afterListView: QListView

    usedResourcesTableView: QTableView
    newResourcesTableView: QTableView

    def __init__(self, task: Task, action: Optional[Action] = None):
        super().__init__()
        uic.loadUi('views/ui/addAction.ui', self)

        self._task = task
        self._new = False

        if action is None:
            action = Action()
            self._new = True
        self._action = action

        self.doneBtn: QPushButton
        self.doneBtn.clicked.connect(self.done_action)

        self.nameLineEdit: QLineEdit
        self.nameLineEdit.setText(action.get_name())
        self.nameLineEdit.textChanged.connect(self.change_name)

        self.durationSpinBox: QSpinBox
        self.durationSpinBox.setValue(action.get_duration())
        self.durationSpinBox.textChanged.connect(self.change_duration)

        # Устанавливаем список исполнителей
        for executor, _ in task.executor_list:
            if executor not in self._action.executor_list:
                self.executorsComboBox.addItem(str(executor), executor)

        executors_model = QStandardItemModel()
        self.executorsListView.setModel(executors_model)
        for executor, _ in action.executor_list:
            item = QStandardItem()
            item.setData(executor.get_name(), Qt.ItemDataRole.DisplayRole)
            item.setData(executor, Qt.ItemDataRole.UserRole)
            executors_model.appendRow(item)

        self.addExecutorBtn: QPushButton
        self.addExecutorBtn.clicked.connect(self.add_executor)
        self.deleteExecutorBtn: QPushButton
        self.deleteExecutorBtn.clicked.connect(self.remove_executor)

        # Устанавливаем список ресурсов
        for resource, _ in task.resource_list:
            self.resourcesComboBox.addItem(str(resource), resource)

        # - Используемые ресурсы
        used_resources_model = QStandardItemModel()
        self.usedResourcesTableView.setModel(used_resources_model)
        used_resources_model.setHorizontalHeaderLabels(['Ресурс', 'Количество'])
        for resource, count in action.required_resource_list:
            name = QStandardItem(str(resource))
            c = QStandardItem()
            c.setData(count, Qt.ItemDataRole.DisplayRole)
            used_resources_model.appendRow([name, c])
        used_resources_model.dataChanged.connect(self.used_resources_table_changed)

        self.addUsedResourceBtn: QPushButton
        self.addUsedResourceBtn.clicked.connect(self.add_used_resources_row)
        self.deleteUsedResourceBtn: QPushButton
        self.deleteUsedResourceBtn.clicked.connect(self.remove_used_resources_rows)

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
        new_resources_model.dataChanged.connect(self.new_resources_table_changed)

        self.addNewResourceBtn: QPushButton
        self.addNewResourceBtn.clicked.connect(self.add_new_resources_row)
        self.deleteNewResourceBtn: QPushButton
        self.deleteNewResourceBtn.clicked.connect(self.remove_new_resources_rows)

        # Устанавливаем список ограничений
        for a in task.action_list:
            if a not in self._action.previous_action_list and a != self._action:
                self.afterComboBox.addItem(str(a), a)

        after_model = QStandardItemModel()
        self.afterListView.setModel(after_model)
        # print(action.previous_action_list)
        for action in action.previous_action_list:
            item = QStandardItem()
            item.setData(action.get_name(), Qt.ItemDataRole.DisplayRole)
            item.setData(action, Qt.ItemDataRole.UserRole)
            after_model.appendRow(item)

        self.addAfterBtn: QPushButton
        self.addAfterBtn.clicked.connect(self.add_after)
        self.deleteAfterBtn: QPushButton
        self.deleteAfterBtn.clicked.connect(self.remove_after)

    def change_name(self):
        self._action.set_name(self.nameLineEdit.text())

    def change_duration(self):
        self.durationSpinBox: QSpinBox
        self._action.set_duration(self.durationSpinBox.value())

    def add_executor(self):
        executor = self.executorsComboBox.currentData(Qt.ItemDataRole.UserRole)
        if executor is None:
            return

        self.executorsComboBox.removeItem(self.executorsComboBox.currentIndex())
        self._action.executor_list.add(executor)

        item = QStandardItem(str(executor))
        item.setData(executor, Qt.ItemDataRole.UserRole)
        self.executorsListView.model().appendRow(item)

    def remove_executor(self):
        selected_indexes = self.executorsListView.selectedIndexes()
        model = self.executorsListView.model()
        if len(selected_indexes) == 0:
            return
        rows_to_remove = []
        for index in selected_indexes:
            rows_to_remove.append(index.row())
        rows_to_remove = list(set(rows_to_remove))
        for row in reversed(sorted(rows_to_remove)):
            ex = model.data(model.index(row, 0), Qt.ItemDataRole.UserRole)
            self._action.executor_list.remove(ex)
            self.executorsListView.model().removeRow(row)
            self.executorsComboBox.addItem(str(ex), ex)

    def add_after(self):
        action = self.afterComboBox.currentData(Qt.ItemDataRole.UserRole)
        if action is None:
            return

        self.afterComboBox.removeItem(self.afterComboBox.currentIndex())
        self._action.previous_action_list.append(action)

        item = QStandardItem(str(action))
        item.setData(action, Qt.ItemDataRole.UserRole)
        self.afterListView.model().appendRow(item)

    def remove_after(self):
        selected_indexes = self.afterListView.selectedIndexes()
        model = self.afterListView.model()
        if len(selected_indexes) == 0:
            return
        rows_to_remove = []
        for index in selected_indexes:
            rows_to_remove.append(index.row())
        rows_to_remove = list(set(rows_to_remove))
        for row in reversed(sorted(rows_to_remove)):
            action = model.data(model.index(row, 0), Qt.ItemDataRole.UserRole)
            self._action.previous_action_list.remove(action)
            self.afterListView.model().removeRow(row)
            self.afterComboBox.addItem(str(action), action)

    def add_used_resources_row(self):
        resource = self.resourcesComboBox.currentData(Qt.ItemDataRole.UserRole)
        if resource is None:
            return

        resources_model = self.usedResourcesTableView.model()
        index = self._action.required_resource_list.get_index(resource)

        if index is not None:
            self._action.required_resource_list.add(resource, 1)
            count = self._action.required_resource_list[resource]
            resources_model.setData(resources_model.index(index, 1), count)
            return

        row = resources_model.rowCount()

        self._action.required_resource_list.add(resource, 1)

        resources_model.insertRow(row)
        resources_model.setData(resources_model.index(row, 0), str(resource), Qt.ItemDataRole.DisplayRole)
        resources_model.setData(resources_model.index(row, 1), 1)

    def remove_used_resources_rows(self):
        selected_indexes = self.usedResourcesTableView.selectedIndexes()
        if len(selected_indexes) == 0:
            return
        rows_to_remove = []
        for index in selected_indexes:
            rows_to_remove.append(index.row())
        rows_to_remove = list(set(rows_to_remove))
        for row in reversed(sorted(rows_to_remove)):
            self._action.required_resource_list.remove_by_index(row)
            self.usedResourcesTableView.model().removeRow(row)

    def used_resources_table_changed(self, start: QModelIndex, end: QModelIndex):
        for row in range(start.row(), end.row() + 1):
            r, count = self._action.required_resource_list.get_by_index(row)
            r: Resource
            for col in range(start.column(), end.column() + 1):
                index = self.usedResourcesTableView.model().index(row, col)
                value = self.usedResourcesTableView.model().data(index, Qt.ItemDataRole.DisplayRole)
                if col == 0:
                    r.set_name(value)
                elif col == 1:
                    self._action.required_resource_list.set_count(r, value)

    def add_new_resources_row(self):
        resource = self.resourcesComboBox.currentData(Qt.ItemDataRole.UserRole)
        if resource is None:
            return

        resources_model = self.newResourcesTableView.model()
        index = self._action.result_resource_list.get_index(resource)

        if index is not None:
            self._action.result_resource_list.add(resource, 1)
            count = self._action.result_resource_list[resource]
            resources_model.setData(resources_model.index(index, 1), count)
            return

        row = resources_model.rowCount()

        self._action.result_resource_list.add(resource, 1)

        resources_model.insertRow(row)
        resources_model.setData(resources_model.index(row, 0), str(resource), Qt.ItemDataRole.DisplayRole)
        resources_model.setData(resources_model.index(row, 1), 1)

    def remove_new_resources_rows(self):
        selected_indexes = self.newResourcesTableView.selectedIndexes()
        if len(selected_indexes) == 0:
            return
        rows_to_remove = []
        for index in selected_indexes:
            rows_to_remove.append(index.row())
        rows_to_remove = list(set(rows_to_remove))
        for row in reversed(sorted(rows_to_remove)):
            self._action.result_resource_list.remove_by_index(row)
            self.newResourcesTableView.model().removeRow(row)

    def new_resources_table_changed(self, start: QModelIndex, end: QModelIndex):
        for row in range(start.row(), end.row() + 1):
            r, count = self._action.result_resource_list.get_by_index(row)
            r: Resource
            for col in range(start.column(), end.column() + 1):
                index = self.newResourcesTableView.model().index(row, col)
                value = self.newResourcesTableView.model().data(index, Qt.ItemDataRole.DisplayRole)
                if col == 0:
                    r.set_name(value)
                elif col == 1:
                    self._action.result_resource_list.set_count(r, value)

    def done_action(self):
        if self.nameLineEdit.text() == '':
            dlg = QMessageBox()
            dlg.setText('Имя не может быть пустым!')
            dlg.exec()
            return

        if self._new:
            self._task.action_list.append(self._action)
        self.close()
