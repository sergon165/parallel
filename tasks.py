from actions import ActionList
from executors import ExecutorList
from resources import ResourceList
from settings import Settings


class Task:
    def __init__(self, description: str = ''):
        self._description: str = description
        self.action_list: ActionList = ActionList()
        self.resource_list: ResourceList = ResourceList()
        self.executor_list: ExecutorList = ExecutorList()
        self.settings: Settings = Settings()

    def get_description(self) -> str:
        return self._description

    def set_description(self, description: str):
        self._description = description

    def get_executor_count(self) -> int:
        executor_count = 0
        for (executor, count) in self.executor_list:
            executor_count += count
        return executor_count

    def __str__(self):
        description = self.get_description()
        if len(description) < 10:
            return description
        return description[:10] + '...'
