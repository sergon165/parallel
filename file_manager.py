import pickle
from typing import Optional

from tasks import Task


class FileManager:
    @staticmethod
    def save(task: Task, src: str):
        file = open(src, 'wb')
        pickle.dump(task, file)
        file.close()

    @staticmethod
    def load(src: str) -> Optional[Task]:
        file = open(src, 'rb')
        try:
            task = pickle.load(file)
        except:
            task = None
        file.close()
        return task
