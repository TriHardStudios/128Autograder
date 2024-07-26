from queue import Queue, SimpleQueue
from typing import Dict, List

from Tasks import Task
from Tasks.common import TaskAlreadyExists, TaskDoesNotExist


class TaskRunner:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.order: SimpleQueue[str] = SimpleQueue()

    def add(self, task: Task):
        if task.getName() in self.tasks:
            raise TaskAlreadyExists(task.getName())

        self.tasks[task.getName()] = task
        self.order.put(task.getName())

    def getResult(self, taskName: str) -> object:
        if taskName not in self.tasks:
            raise TaskDoesNotExist(taskName)

        return self.tasks[taskName].getResult()


    def run(self):
        while not self.order.empty():
            task: Task = self.tasks[self.order.get()]

            task.doTask()

            if task.getStatus():
                break
