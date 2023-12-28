from configparser import ConfigParser
from time import sleep

from job import Job
from logger import logger
from types import (
    Request,
    Response,
    ResponseStatus
)


class Scheduler:
    def __init__(self, pool_size: int=10) -> None:
        self.__pool_size: list[Job] = pool_size
        self.__pending: list[Job] = []
        self.__pool: list[Job] = []
        self.__ready: list[Job] = []

        config = ConfigParser()
        config.read('setup.cfg')
        self.__tick = float(config['scheduler']['tick'])

    def schedule(self, task: Job) -> None:
        self.__pending.append(task)

    def run(self):
        while True:
            sleep(self.__tick)
            space = self.__pool_size - len(self.__pool)  # must be >=0
            if space and self.__pending:
                task = self.__pending.pop(0)
                task()
                self.__pool.append(task)
            if not self.__pool:
                continue  # so, it will sleep for a __tick again
            finish: list[int] = []
            for (i, task) in enumerate(self.__pool):
                task.send(Request.status)
                response: Response = next(task)
                if response.status is ResponseStatus.progress:
                    pass
                if response.status is ResponseStatus.result:
                    logger.debug(f"{task.get_id()}: {response.new_results}")
                if response.status is ResponseStatus.finish:
                    finish.append(i)

            for i in finish:
                task = self.__pool.pop(i)
                self.__ready.append(task)

    def restart(self):
        pass

    def stop(self):
        pass
