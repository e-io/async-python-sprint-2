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
            logger.debug("the begin of main 'while' cycle")
            sleep(self.__tick)
            space = self.__pool_size - len(self.__pool)  # must be >=0

            for _ in range(space):
                if not self.__pending:  # not targets anymore
                    break
                job = self.__pending.pop(0)
                job.run()
                logger.debug(f"Initial calling of 'next' for a job with id '{job.get_id()}'")
                next(job.loop)
                self.__pool.append(job)

            if not self.__pool:
                break  # no job anymore

            finished: list[int] = []  # indices of finished jobs
            for (i, job) in enumerate(self.__pool):
                logger.debug(f"A call of 'next' for {job.get_id()}")
                next(job.loop)
                logger.debug(f"Sending request to {job.get_id()}")
                response: Response = job.loop.send(Request.report_status)
                # logger.debug(f"A call of 'next' for {job.get_id()}")
                # next(job.loop)
                logger.debug(f"Scheduler got response '{response.status.value}'")

                if response.status is ResponseStatus.waiting:
                    continue
                if response.status is ResponseStatus.result:
                    logger.debug(f"Scheduler got result  '{response.new_results}' from {job.get_id()}")
                    continue
                if response.status is ResponseStatus.finish:
                    finished.append(i)

            for i in finished:
                job = self.__pool[i]
                self.__ready.append(job)
            for i in finished[::-1]:
                self.__pool.pop(i)

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
