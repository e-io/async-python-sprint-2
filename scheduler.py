from configparser import ConfigParser
from threading import Thread, Event
from time import sleep

from job import Job
from logger import logger
from customtypes import (
    Request,
    Response,
    ResponseStatus
)


class Scheduler:
    """
    A class used to represent a Scheduler.
    It may contain several jobs inside.

    Attributes
    ----------
    __pending : list[Job]
        jobs which are waiting to be in the pool
    __pool : list[Job]
        jobs which are in the progress
    __ready : list[Job]
        jobs which are done
    __tick : float
        something like 'a frequency' of the whole project in seconds
    """
    def __init__(self, pool_size: int = 10) -> None:
        self.__pool_size: int = pool_size
        self.__pending: list[Job] = []
        self.__pool: list[Job] = []
        self.__ready: list[Job] = []
        # by safeword it is meaning a signal to stop all processes and make a backup
        self.safeword = Event()
        self.thread = Thread(target=self.__run)  # main thread for a main loop

        config = ConfigParser()
        config.read('setup.cfg')
        self.__tick = float(config['scheduler']['tick'])

    def schedule(self, job: Job) -> None:
        """Add a job in the list of pending jobs."""
        self.__pending.append(job)

    def run(self) -> None:
        self.safeword.clear()  # just for explicit behaviour
        self.thread.start()
        # The thread will be stopped by itself.
        # There is no need in additional actions.

    def stop(self) -> None:
        """Stop all jobs and backup there condition."""
        logger.debug("Event 'safeword' is set")
        self.safeword.set()

    def __run(self) -> None:
        """Do jobs. This is the main loop of the whole class."""
        while True:
            sleep(self.__tick)
            logger.debug("The first line of main 'while' cycle of Scheduler.")
            if self.safeword.is_set():
                self.__backup()
                exit(0)  # It's shown explicitly that the current thread finishes its work

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
        """Start all jobs again where they were stopped."""
        ...

    def __backup(self) -> None:
        """A stub"""
        logger.debug("This is '__backup' function'")
        sleep(self.__tick)

    def __restore(self) -> None:
        """A stub"""
        ...
