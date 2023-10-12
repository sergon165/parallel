from typing import Optional, Tuple

from PyQt6 import uic
from PyQt6.QtCore import QSize, QPoint, Qt, QModelIndex
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QLabel, QPlainTextEdit, QWidget, QTableView, QItemDelegate, QCheckBox, \
    QTableWidget, QPushButton, QButtonGroup, QRadioButton, QFileDialog, QSpinBox

from executors import Executor, ExecutorList
from file_manager import FileManager
from resources import Resource
from tasks import Task
from views.action_widget import ActionWidget
from views.action_dialog import ActionDialog


class ConstructorWindow(QMainWindow):
    executorsSpinBox: QSpinBox
    descriptionTextEdit: QPlainTextEdit

    def __init__(self, task: Optional[Task] = None, src: str = '', size: Optional[QSize] = None,
                 pos: Optional[QPoint] = None):
        super().__init__()
        uic.loadUi('views/ui/constructor.ui', self)

        self._open_menu = True
        self._src = src
        self._default_title = self.windowTitle()
        self.set_title()

        self._saved_executors = None

        # Устанавливаем менюбар
        self._set_menubar()

        # Устанавливаем значение task
        if task is not None:
            self._task = task
        else:
            self._task = Task()

        # Устанавливаем данные
        self._executors_table: QTableView = self.findChild(QTableView, 'executorsTable')
        self._resources_table: QTableView = self.findChild(QTableView, 'resourcesTable')
        self.set_task()

        # Реализуем работу вкладки ресурсов
        self.findChild(QPushButton, 'addResourceBtn').clicked.connect(self.add_resources_row)
        self.findChild(QPushButton, 'deleteResourceBtn').clicked.connect(self.remove_resources_rows)
        use_resources: QCheckBox = self.findChild(QCheckBox, 'useResourcesCheckBox')
        use_resources.stateChanged.connect(self.use_resources_changed)
        self._resources_table.model().dataChanged.connect(self.resources_table_changed)

        # Реализуем работу вкладки исполнителей
        self.findChild(QPushButton, 'addExecutorBtn').clicked.connect(self.add_executors_row)
        self.findChild(QPushButton, 'deleteExecutorBtn').clicked.connect(self.remove_executors_rows)
        executor_button_group: QButtonGroup = self.findChild(QButtonGroup, 'executorButtonGroup')
        executor_button_group.buttonClicked.connect(self.executor_button_clicked)
        self._executors_table.model().dataChanged.connect(self.executor_table_changed)

        # Реализуем работу действий
        self.findChild(QPushButton, 'addActionBtn').clicked.connect(self.add_action)

        self.descriptionTextEdit.textChanged.connect(self.description_changed)
        self.executorsSpinBox.textChanged.connect(self.executor_count_changed)

        # Изменяем размер окна
        if size:
            self.resize(size)
        if pos:
            self.move(pos)

    def set_title(self):
        if self._src != '':
            self.setWindowTitle(self._default_title + ' - ' + self._src)
        else:
            self.setWindowTitle(self._default_title)

    def _set_menubar(self):
        execute_mode: QAction = self.findChild(QAction, 'executeModeAction')
        execute_mode.triggered.connect(self.enter_execute_mode)
        self.findChild(QAction, 'saveAction').triggered.connect(self.save)
        self.findChild(QAction, 'saveAsAction').triggered.connect(self.save_as)
        self.findChild(QAction, 'createAction').triggered.connect(self.create_action)
        self.findChild(QAction, 'openAction').triggered.connect(self.open)

    def enter_execute_mode(self):
        from views.task import TaskWindow
        self._open_menu = False
        self._task_window = TaskWindow(self._task, self._src, self.size(), self.pos())
        self.close()
        self._task_window.show()

    def description_changed(self):
        self._task.set_description(self.descriptionTextEdit.toPlainText())

    def use_resources_changed(self):
        use_resources: QCheckBox = self.findChild(QCheckBox, 'useResourcesCheckBox')
        resources_widget: QWidget = self.findChild(QWidget, 'resourcesTableWidget')
        resources_table: QTableView = self.findChild(QTableView, 'resourcesTable')
        state = True if use_resources.checkState() == Qt.CheckState.Checked else False
        self._task.settings.resources_enabled = state
        resources_widget.setEnabled(state)
        resources_table.setEnabled(state)

    def executor_button_clicked(self, button: QRadioButton):
        universal: QWidget = self.findChild(QWidget, 'universalContentWidget')
        specific: QWidget = self.findChild(QWidget, 'executorsTableWidget')
        specific_table: QTableView = self.findChild(QTableView, 'executorsTable')
        use_specific = True if button.objectName() == 'specificRadioBtn' else False
        self._task.settings.specific_executors_enabled = use_specific
        universal.setEnabled(not use_specific)
        specific.setEnabled(use_specific)
        specific_table.setEnabled(use_specific)

        if use_specific:
            if self._saved_executors is not None:
                self._task.executor_list = self._saved_executors
        else:
            self._saved_executors = self._task.executor_list
            self._universal_executer = Executor('Исполнитель')
            self._task.executor_list = ExecutorList()
            self._task.executor_list.set_count(self._universal_executer, self.executorsSpinBox.value())

    def executor_count_changed(self):
        self._task.executor_list.set_count(self._universal_executer, self.executorsSpinBox.value())

    def set_task(self):
        task = self._task

        # Устанавливаем описание задания
        self.findChild(QPlainTextEdit, 'descriptionTextEdit').setPlainText(task.get_description())

        # Устанавливаем вкладку списка ресурсов
        # - Устанавливаем значение чекбокса
        use_resources: QCheckBox = self.findChild(QCheckBox, 'useResourcesCheckBox')
        state = Qt.CheckState.Checked if self._task.settings.resources_enabled else Qt.CheckState.Unchecked
        use_resources.setCheckState(state)
        self.use_resources_changed()

        # - Заполняем таблицу
        resources_model = QStandardItemModel()
        resources_model.setColumnCount(3)
        resources_model.setHorizontalHeaderLabels(['Название', 'Расходуемый', 'Количество'])
        self._resources_table.setModel(resources_model)
        delegate = ResourceItemDelegate(self._resources_table)
        self._resources_table.setItemDelegateForColumn(1, delegate)

        row = 0
        for (r, count) in task.resource_list:
            name = QStandardItem()
            name.setData(r.get_name(), Qt.ItemDataRole.DisplayRole)
            resources_model.setItem(row, 0, name)

            consumable = QStandardItem()
            consumable.setData(r.is_consumable(), Qt.ItemDataRole.DisplayRole)
            resources_model.setItem(row, 1, consumable)

            count_item = QStandardItem()
            count_item.setData(count, Qt.ItemDataRole.DisplayRole)
            resources_model.setItem(row, 2, count_item)

            row += 1

        # Устанавливаем список исполнителей
        if not self._task.settings.resources_enabled:
            self.executorsSpinBox.setValue(self._task.executor_list.get_total_count())
        # - Устанавливаем значение радиокнопки
        universal_radio_button: QRadioButton = self.findChild(QRadioButton, 'universalRadioBtn')
        specific_radio_button: QRadioButton = self.findChild(QRadioButton, 'specificRadioBtn')
        if self._task.settings.specific_executors_enabled:
            specific_radio_button.setChecked(True)
            self.executor_button_clicked(specific_radio_button)
        else:
            universal_radio_button.setChecked(True)
            self.executor_button_clicked(universal_radio_button)

        # - Заполняем таблицу
        executors_model = QStandardItemModel()
        executors_model.setColumnCount(2)
        executors_model.setHorizontalHeaderLabels(['Название', 'Количество'])
        self._executors_table.setModel(executors_model)

        if self._task.settings.specific_executors_enabled:
            row = 0
            for (executor, count) in self._task.executor_list:
                ex = QStandardItem()
                ex.setData(executor.get_name(), Qt.ItemDataRole.DisplayRole)
                executors_model.setItem(row, 0, ex)

                c = QStandardItem()
                c.setData(count, Qt.ItemDataRole.DisplayRole)
                executors_model.setItem(row, 1, c)

                row += 1

        # Устанавливаем список действий
        action_container: QWidget = self.findChild(QWidget, 'actionScrollAreaWidgetContents')
        layout = action_container.layout()
        for i in range(layout.count()):
            widget: QWidget = layout.takeAt(i).widget()
            widget.deleteLater()
        for action in task.action_list:
            action_widget = ActionWidget(action, task.settings, True, self._task, self.set_task)
            layout.addWidget(action_widget)

    def add_resources_row(self):
        resources_model = self._resources_table.model()
        row = resources_model.rowCount()
        name = f'Ресурс{row + 1}'

        new_resource = Resource(name)
        new_resource.set_consumable(True)
        self._task.resource_list.add(new_resource)

        resources_model.insertRow(row)
        resources_model.setData(resources_model.index(row, 0), name)
        resources_model.setData(resources_model.index(row, 1), True)
        resources_model.setData(resources_model.index(row, 2), 0)

    def remove_resources_rows(self):
        selected_indexes = self._resources_table.selectedIndexes()
        if len(selected_indexes) == 0:
            return
        rows_to_remove = []
        for index in selected_indexes:
            rows_to_remove.append(index.row())
        rows_to_remove = list(set(rows_to_remove))
        for row in reversed(sorted(rows_to_remove)):
            self._task.resource_list.remove_by_index(row)
            self._resources_table.model().removeRow(row)

    def resources_table_changed(self, start: QModelIndex, end: QModelIndex):
        for row in range(start.row(), end.row() + 1):
            r, count = self._task.resource_list.get_by_index(row)
            r: Resource
            for col in range(start.column(), end.column() + 1):
                index = self._resources_table.model().index(row, col)
                value = self._resources_table.model().data(index, Qt.ItemDataRole.DisplayRole)
                if col == 0:
                    r.set_name(value)
                elif col == 1:
                    r.set_consumable(value)
                elif col == 2:
                    self._task.resource_list.set_count(r, value)

    def add_executors_row(self):
        executors_model = self._executors_table.model()
        row = executors_model.rowCount()
        name = f'Исполнитель{row + 1}'

        new_executor = Executor(name)
        self._task.executor_list.add(new_executor, 1)

        executors_model.insertRow(row)
        executors_model.setData(executors_model.index(row, 0), name)
        executors_model.setData(executors_model.index(row, 1), 1)

    def remove_executors_rows(self):
        selected_indexes = self._executors_table.selectedIndexes()
        if len(selected_indexes) == 0:
            return
        rows_to_remove = []
        for index in selected_indexes:
            rows_to_remove.append(index.row())
        rows_to_remove = list(set(rows_to_remove))
        for row in reversed(sorted(rows_to_remove)):
            self._task.executor_list.remove_by_index(row)
            self._executors_table.model().removeRow(row)

    def executor_table_changed(self, start, end):
        for row in range(start.row(), end.row() + 1):
            ex, count = self._task.executor_list.get_by_index(row)
            ex: Executor
            for col in range(start.column(), end.column() + 1):
                index = self._executors_table.model().index(row, col)
                value = self._executors_table.model().data(index, Qt.ItemDataRole.DisplayRole)
                if col == 0:
                    ex.set_name(value)
                elif col == 1:
                    self._task.executor_list.set_count(ex, value)

    def add_action(self):
        add_action_dialog = ActionDialog(self._task)
        add_action_dialog.exec()
        self.set_task()

    def create_action(self):
        self._src = ''
        self.set_title()
        self._task = Task()
        self.set_task()

    def save(self):
        if self._src != '':
            FileManager.save(self._task, self._src)
        else:
            self.save_as()

    def save_as(self):
        src, _ = QFileDialog.getSaveFileName()
        FileManager.save(self._task, src)
        self._src = src
        self.set_title()

    def open(self):
        src, _ = QFileDialog.getOpenFileName()
        if src != '':
            task = FileManager.load(src)
            self._src = src
            self._task = task
            self._saved_executors = task.executor_list
            self.set_title()
            self.set_task()

    def closeEvent(self, e):
        from views.menu import MenuWindow
        self._menu_window = MenuWindow()
        if self._open_menu:
            self._menu_window.show()
        e.accept()


class ResourceItemDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        value = Qt.CheckState.Checked if index.data() else Qt.CheckState.Unchecked
        self.drawCheck(painter, option, option.rect, value)

    def createEditor(self, parent, option, index):
        checkbox = QCheckBox(parent)
        return checkbox

    def setEditorData(self, editor: QCheckBox, index) -> None:
        value = index.data()
        if value:
            editor.setCheckState(Qt.CheckState.Checked)
        else:
            editor.setCheckState(Qt.CheckState.Unchecked)

    def setModelData(self, editor: QCheckBox, model, index):
        value = editor.checkState()
        if value == Qt.CheckState.Checked:
            model.setData(index, True)
        else:
            model.setData(index, False)
