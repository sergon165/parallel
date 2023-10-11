import pickle

from tasks import Task


class FileManager:
    @staticmethod
    def save(task: Task, src: str):
        file = open(src, 'wb')
        pickle.dump(task, file)
        file.close()

    @staticmethod
    def load(src: str) -> Task:
        file = open(src, 'rb')
        task = pickle.load(file)
        file.close()
        return task
