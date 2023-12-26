from typing import Callable

from logger import logger


class Job:
    all_id: dict = {}  # str: int

    def __init__(self, target: Callable, start_at="", max_working_time=-1, tries=0, dependencies=[], *args, **kwargs):
        self._gen = target(*args, **kwargs)
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies

        name = target.__name__
        if name in Job.all_id.keys():
            Job.all_id[name] += 1
        else:
            Job.all_id[name] = 1
        self._id = name + '_' + str(Job.all_id[name])

    def get_id(self):
        return self._id

    def run(self):
        try:
            while True:
                result = next(self._gen)
                logger.info(f"{self._id}: {result}")
        except StopIteration:
            pass

    def pause(self):
        pass

    def stop(self):
        pass
