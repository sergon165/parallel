from typing import List

from executors import ExecutorList
from resources import ResourceList


class Action:
    def __init__(self, name: str = '', duration: int = 1):
        self._name: str = name
        self._duration: int = duration
        self.required_resource_list: ResourceList = ResourceList()
        self.result_resource_list: ResourceList = ResourceList()
        self.executor_list: ExecutorList = ExecutorList()
        self.previous_action_list: ActionList = ActionList()

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_duration(self) -> int:
        return self._duration

    def get_duration_str(self) -> str:
        duration = self._duration
        units = duration % 10
        dozens = duration % 100 // 10
        res = f'{duration} '

        if dozens == 1 or units == 0 or units >= 5:
            return res + 'тактов'
        if units == 1:
            return res + 'такт'
        return res + 'такта'

    def set_duration(self, duration: int):
        self._duration = duration

    def __str__(self):
        return self.get_name()


class ActionList:
    def __init__(self):
        self._action_list: List[Action] = []

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._action_list):
            action = self._action_list[self._index]
            self._index += 1
            return action
        raise StopIteration

    def __getitem__(self, item):
        return self._action_list[item]

    def __len__(self):
        return len(self._action_list)

    def __str__(self):
        res = ''
        for a in self._action_list:
            res += str(a) + ', '
        res = res[:-2]
        return res

    def append(self, a: Action):
        self._action_list.append(a)

    def remove(self, a: Action):
        self._action_list.remove(a)

    def get_all(self) -> List[Action]:
        return self._action_list
