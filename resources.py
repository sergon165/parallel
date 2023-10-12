from typing import List, Dict, Optional


class Resource:
    def __init__(self, name: str, consumable: bool = True):
        self._name: str = name
        # self._count: int = count
        self._consumable: bool = consumable

    def __str__(self):
        res = self.get_name()
        if not (self.is_consumable()):
            res += '*'
        return res

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: int):
        self._name = name

    def is_consumable(self) -> bool:
        return self._consumable

    def set_consumable(self, value: bool):
        self._consumable = value


class ResourceList:
    def __init__(self):
        self._resource_list: Dict[Resource, int] = {}

    def __iter__(self):
        self._items = list(self._resource_list.items())
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._items):
            key, value = self._items[self._index]
            self._index += 1
            return key, value
        raise StopIteration

    def __getitem__(self, item):
        return self._resource_list[item]

    def __len__(self):
        return len(self._resource_list)

    def __str__(self):
        res = ''
        for r in self._resource_list.items():
            if r[1] > 0:
                res += str(r[0])
                if r[1] > 1:
                    res += f' ({r[1]} шт.)'
                res += ', '
        res = res[:-2]
        return res

    def set_resource_list(self, rl: Dict[Resource, int]):
        self._resource_list = rl

    def add(self, resource: Resource, count: int = 0):
        if resource in self._resource_list:
            self._resource_list[resource] += count
        else:
            self._resource_list[resource] = count

    def sub(self, resource: Resource, count: int = 1):
        if resource in self._resource_list:
            self._resource_list[resource] -= count

    def set_count(self, resource: Resource, count: int):
        if resource in self._resource_list:
            self._resource_list[resource] = count

    def remove(self, resource: Resource):
        self._resource_list.pop(resource)

    def remove_by_index(self, index: int):
        items = list(self._resource_list.keys())
        self._resource_list.pop(items[index])

    def get_all(self) -> Dict[Resource, int]:
        return self._resource_list

    def get_by_index(self, index: int):
        items = list(self._resource_list.items())
        return items[index]

    def get_index(self, resource: Resource) -> Optional[int]:
        if resource in self._resource_list:
            return list(self._resource_list.keys()).index(resource)
        return None
