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
    def __init__(self, pool_size: int = 10) -> None:
        self.__pool_size: int = pool_size
        self.__pending: list[Job] = []
        self.__pool: list[Job] = []
        self.__ready: list[Job] = []

        config = ConfigParser()
        config.read('setup.cfg')
        self.__tick = float(config['scheduler']['tick'])

    def schedule(self, job: Job) -> None:
        self.__pending.append(job)

    def run(self) -> None:
        while True:
            logger.debug('')
            sleep(self.__tick)
            space = self.__pool_size - len(self.__pool)  # must be >=0

            if space and self.__pending:
                job = self.__pending.pop(0)
                job.run()
                next(job.loop)
                self.__pool.append(job)

            if not self.__pool:
                break  # no job anymore

            finish: list[int] = []
            for (i, job) in enumerate(self.__pool):
                logger.debug('here')
                next(job.loop)
                job.loop.send(Request.report_status)
                logger.debug('here1')
                response: Response = next(job.loop)
                logger.debug(f'Scheduler got response "{response.status.value}"')
                if response.status is ResponseStatus.waiting:
                    continue
                if response.status is ResponseStatus.result:
                    logger.debug(f"Scheduler got result  {response.new_results} from {job.loop.get_id()}")

                if response.status is ResponseStatus.finish:
                    finish.append(i)

            for i in sorted(finish, reverse=True):
                job = self.__pool.pop(i)
                self.__ready.append(job)
        logger.debug(f"Scheduler finished its work. "
                     f"Finished jobs: {len(self.__ready)}")

    def restart(self) -> None:
        ...

    def stop(self) -> None:
        ...

    def __backup(self) -> None:
        ...

    def __restore(self) -> None:
        ...
