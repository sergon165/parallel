from typing import List, Dict


class Executor:
    def __init__(self, name: str):
        self._name: str = name

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def __str__(self):
        return self.get_name()


class ExecutorList:
    def __init__(self):
        self._executor_list: Dict[Executor, int] = {}

    def __iter__(self):
        self._items = list(self._executor_list.items())
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._items):
            key, value = self._items[self._index]
            self._index += 1
            return key, value
        raise StopIteration

    def __getitem__(self, item):
        return self._executor_list[item]

    def __contains__(self, item):
        return item in self._executor_list

    def __len__(self):
        return len(self._executor_list)

    def __str__(self):
        res = ''
        for ex in self._executor_list.items():
            res += str(ex[0]) + ', '
        res = res[:-2]
        return res

    def add(self, ex: Executor, count: int = 1):
        if ex in self._executor_list:
            self._executor_list[ex] += count
        else:
            self._executor_list[ex] = count

    def sub(self, ex: Executor, count: int = 1):
        if ex in self._executor_list:
            self._executor_list[ex] -= count

    def set_count(self, ex: Executor, count: int):
        self._executor_list[ex] = count

    def remove(self, ex: Executor):
        self._executor_list.pop(ex)

    def remove_by_index(self, index: int):
        keys = list(self._executor_list.keys())
        self._executor_list.pop(keys[index])

    def get_total_count(self):
        total_count = 0
        for _, count in self._executor_list.items():
            total_count += count
        return total_count

    def get_all(self) -> Dict[Executor, int]:
        return self._executor_list

    def get_by_index(self, index: int):
        items = list(self._executor_list.items())
        return items[index]
