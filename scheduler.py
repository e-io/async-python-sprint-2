from configparser import ConfigParser
from time import sleep

from job import Job
from logger import logger
from customtypes import (
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

    def schedule(self, job: Job) -> None:
        self.__pending.append(job)

    def run(self):
        while True:
            logger.debug('')
            sleep(self.__tick)
            space = self.__pool_size - len(self.__pool)  # must be >=0
            if space and self.__pending:
                job = self.__pending.pop(0)
                loop = job.loop()
                next(loop)
                #logger.debug(f'debuuuuug {type(job.loop)}')
                #exit(1)
                self.__pool.append(loop)
            if not self.__pool:
                continue  # so, it will sleep for a __tick again
            finish: list[int] = []
            for (i, loop) in enumerate(self.__pool):
                logger.debug('here')
                next(loop)
                loop.send(Request.report_status)
                logger.debug('here1')
                response: Response = next(loop)
                if response.status is ResponseStatus.waiting:
                    pass
                if response.status is ResponseStatus.result:
                    logger.debug(f"{loop.get_id()}: {response.new_results}")
                if response.status is ResponseStatus.finish:
                    finish.append(i)

            for i in finish:
                job = self.__pool.pop(i)
                self.__ready.append(job)

    def restart(self):
        pass

    def stop(self):
        pass
