import copy
from typing import List, Optional, Dict, Tuple
from actions import Action
from executors import Executor
from resources import Resource, ResourceList
from tasks import Task


class Timetable:
    def __init__(self, task: Task):
        self._task = task
        self._timetable: List[List[Optional[Action]]] = []
        self._clock_count = 0
        self.add_clock()

    def add_clock(self, count: int = 1):
        for i in range(count):
            clock = []
            for j in range(self._task.get_executor_count()):
                clock.append(None)
            self._timetable.append(clock)
            self._clock_count += 1

    def remove_clock(self, index: int):
        self._timetable.pop(index)
        self._clock_count -= 1

    def remove_empty(self):
        for i in range(len(self._timetable) - 1, -1, -1):
            empty = True
            for j in range(len(self._timetable[i])):
                if self._timetable[i][j] is not None:
                    empty = False
                    break
            if not empty:
                break
            self.remove_clock(i)
        self.add_clock()

    def add_action(self, action: Action, clock: int, executor: int):
        for i in range(action.get_duration()):
            current_clock = clock + i
            if current_clock == self._clock_count:
                self.add_clock()
            self._timetable[current_clock - 1][executor - 1] = action

    def remove_action(self, action: Action):
        for i in range(len(self._timetable)):
            if action in self._timetable[i]:
                index = self._timetable[i].index(action)
                self._timetable[i][index] = None
        self.remove_empty()

    def get_timetable(self) -> List[List[Optional[Action]]]:
        return self._timetable

    def get_clock_count(self) -> int:
        return len(self._timetable)

    def get_executor(self, clock: int) -> Optional[Executor]:
        cur_clock = 0
        for (executor, count) in self._task.executor_list:
            cur_clock += count
            if cur_clock >= clock:
                return executor
        return None

    def check(self) -> List[str]:
        mistakes: List[str] = []
        cur_resources = ResourceList()
        cur_resources.set_resource_list(copy.copy(self._task.resource_list.get_all()))
        remains: Dict[Action, int] = {}
        for action in self._task.action_list:
            remains[action] = action.get_duration()

        for (i, clock) in enumerate(self._timetable):
            # Ресурсы, которые будут добавлены после выполнения такта
            add_resources = ResourceList()

            # Законченные в этом такте действия
            ended_actions: List[Action] = []

            for (j, action) in enumerate(clock):
                if action is not None:

                    # Если действие только началось
                    if remains[action] == action.get_duration():
                        # Проверяем исполнителя
                        if self.get_executor(j + 1) not in action.executor_list:
                            mistakes.append(f'У действия "{action}" неверно задан исполнитель')

                        # Проверяем выполнение предыдущих заданий
                        for prev in action.previous_action_list:
                            if remains[prev] != 0 or prev in ended_actions:
                                mistakes.append(f'Перед действием "{action}" должно быть выполнено действие "{prev}"')

                        # Забираем ресурсы
                        for (r, count) in action.required_resource_list:
                            cur_resources.sub(r, count)
                            if cur_resources[r] < 0:
                                mistakes.append(f'Для действия "{action}" не хватает ресурса "{r}"')

                    # Вычитаем оставшуюся продолжительность
                    remains[action] -= 1

                    # Если действие закончилось
                    if remains[action] == 0:

                        # Возвращаем непотребляемые ресурсы
                        for (r, count) in action.required_resource_list:
                            if not r.is_consumable():
                                add_resources.add(r, count)

                        # Добавляем новые ресурсы
                        for (r, count) in action.result_resource_list:
                            add_resources.add(r, count)
                        ended_actions.append(action)

            # Отправляем добавленные ресурсы в список текущих ресурсов
            for (r, count) in add_resources:
                cur_resources.add(r, count)

        for (action, left) in remains.items():
            if left > 0:
                mistakes.append(f'Действие "{action}" не назначено никакому исполнителю')

        return mistakes

    def print_timetable(self):
        print(self._timetable)
