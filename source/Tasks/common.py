import enum


class TaskStatus(enum.Enum):
    NOT_STARTED = 1
    RUNNING = 2
    COMPLETE = 3
    ERROR = 4


class FailedToLoadSuppliers(Exception):
    def __init__(self, ex: Exception):
        super().__init__(f"Failed to process input suppliers.\n{ex}")

class AttemptToGetInvalidResults(Exception):
    def __init__(self):
        super().__init__("Attempt to get result from task with: Status != COMPLETE")
