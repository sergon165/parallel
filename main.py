import pickle
import sys
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

from executors import Executor, ExecutorList
from file_manager import FileManager
from resources import Resource, ResourceList
from actions import Action, ActionList
from tasks import Task
from timetable import Timetable

from views.menu import MenuWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        button = QPushButton()
        button.setText('Проверка')

        self.setCentralWidget(button)

        self.setFixedSize(QSize(400, 300))


def get_test_task():
    # Исполнители
    e1 = Executor('Чистельщик')
    e2 = Executor('Варщик')

    # Ресурсы
    potato = Resource('Картофель')
    onion = Resource('Лук')
    carrot = Resource('Морковь')
    clear_potato = Resource('Почищенный картофель')
    clear_onion = Resource('Порезанный лук')
    clear_carrot = Resource('Почищенная морковь')
    knife = Resource('Нож')
    knife.set_consumable(False)
    pot = Resource('Кастрюля')
    pot.set_consumable(False)

    # Действия
    a1 = Action('Почистить картофель')
    a1.executor_list.add(e1)
    a1.required_resource_list.add(potato, 1)
    a1.required_resource_list.add(knife, 1)
    a1.result_resource_list.add(clear_potato, 1)

    a2 = Action('Порезать лук')
    a2.executor_list.add(e1)
    a2.required_resource_list.add(onion, 1)
    a2.required_resource_list.add(knife, 1)
    a2.result_resource_list.add(clear_onion, 1)

    a3 = Action('Порезать морковь')
    a3.executor_list.add(e1)
    a3.required_resource_list.add(carrot, 1)
    a3.required_resource_list.add(knife, 1)
    a3.result_resource_list.add(clear_carrot, 1)

    a4 = Action('Вскипятить воду', 1)
    a4.executor_list.add(e2)
    a4.required_resource_list.add(pot, 1)

    a5 = Action('Добавить картофель в кастрюлю', 2)
    a5.executor_list.add(e2)
    a5.required_resource_list.add(clear_potato, 1)
    a5.required_resource_list.add(pot, 1)
    a5.previous_action_list.append(a4)

    a6 = Action('Добавить зажарку в кастрюлю')
    a6.executor_list.add(e2)
    a6.previous_action_list.append(a5)
    a6.previous_action_list.append(a4)
    a6.required_resource_list.add(clear_onion, 1)
    a6.required_resource_list.add(clear_carrot, 1)
    a6.required_resource_list.add(pot, 1)

    # Задание
    task = Task('Приготовить суп. Для этого понадобится нарезать картошку, лук, морковь, вскипятить воду и добавить '
                'все в кастрюлю.')
    task.settings.resources_enabled = True
    task.settings.specific_executors_enabled = True

    task.action_list.append(a1)
    task.action_list.append(a2)
    task.action_list.append(a3)
    task.action_list.append(a4)
    task.action_list.append(a5)
    task.action_list.append(a6)

    task.resource_list.add(potato, 1)
    task.resource_list.add(clear_potato)
    task.resource_list.add(onion, 1)
    task.resource_list.add(clear_onion)
    task.resource_list.add(carrot, 1)
    task.resource_list.add(clear_carrot)
    task.resource_list.add(knife, 1)
    task.resource_list.add(pot, 2)

    task.executor_list.add(e1, 2)
    task.executor_list.add(e2)

    return task


if __name__ == '__main__':
    task = get_test_task()
    FileManager.save(task, 'soup.task')

    app = QApplication(sys.argv)

    window = MenuWindow()
    window.show()

    app.exec()

