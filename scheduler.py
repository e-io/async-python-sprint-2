from configparser import ConfigParser
from multiprocessing import Process, Queue
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
    The 'official' simple wrap for the class _Scheduler
    """
    def __init__(self, pool_size: int = 10) -> None:
        config = ConfigParser()
        config.read('setup.cfg')
        self.__tick = float(config['scheduler']['tick'])

        self.scheduler = _Scheduler(pool_size=pool_size, tick=self.__tick)
        self.process = None
        self.queue = None

    def schedule(self, job: Job) -> None:
        """Add a job in the list of pending jobs."""
        self.scheduler.schedule(job)

    def run(self) -> None:
        scheduler = self.scheduler
        self.queue = Queue()
        queue = self.queue
        self.process = Process(target=scheduler.run, args=(queue,))
        self.process.start()
        # sleep(10 * self.__tick)
        # self.process.join()

    def stop(self) -> None:
        logger.debug("Scheduler.stop is called")
        self.queue.put('stop')


class _Scheduler:
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
    def __init__(self, pool_size: int, tick: float) -> None:
        self.__pool_size: int = pool_size
        self.__pending: list[Job] = []
        self.__pool: list[Job] = []
        self.__ready: list[Job] = []
        self.__tick: float = tick
        self.queue = None

    def schedule(self, job: Job) -> None:
        """Add a job in the list of pending jobs."""
        self.__pending.append(job)

    def run(self, queue: Queue) -> None:
        self.queue = queue
        self.__run()

    def stop(self) -> None:
        """Stop all jobs and backup their condition."""
        logger.debug("This is _Scheduler.stop()")
        self.__backup()
        exit(0)

    def __run(self) -> None:
        """Do jobs. This is the main loop of the whole class."""
        while True:
            sleep(self.__tick)
            logger.debug("The first line of main 'while' cycle of Scheduler.")

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
                sleep(self.__tick / 4)
                if not self.queue.empty():
                    message = self.queue.get()
                    self.queue.put(message)
                    if message == 'stop':
                        self.stop()
                        break
                    else:
                        pass  # just ignore

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
        ...  # saving the state of all "jobs" in a CSV file

    def __restore(self) -> None:
        """A stub"""
        ...
