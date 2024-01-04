from configparser import ConfigParser
from csv import writer as Csv_writer
from multiprocessing import Process, Queue
from pathlib import Path
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
        """Save the state of all "jobs" in a CSV file"""
        logger.debug("This is '__backup' function'")

        name = 'backup/backup'
        spreadsheet_extension = '.tsv'
        spreadsheet_extension = spreadsheet_extension.lower()
        if spreadsheet_extension not in ('.tsv', '.csv'):
            raise Exception('wrong extension of a spreadsheet')
        path = Path(name)
        if path.suffix != spreadsheet_extension:
            path = path.with_suffix(spreadsheet_extension)
        logger.debug(f'A backup will be saved in the file {path}')
        if path.parent:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w+') as csv_:  # spreadsheet
            delimeter = ';'
            if spreadsheet_extension == '.tsv':
                delimeter = '\t'
            csv_writer = Csv_writer(csv_, delimiter=delimeter)
            header = ['job_id',
                      'status',
                      'start_at',
                      'max_working_time',
                      'tries_left',
                      'dependencies',
                      'pickled',
                      ]
            csv_writer.writerow(header)

            sleep(self.__tick)

            # this is the most correct order for the correct restore later
            for job in [*self.__pool, *self.__pending, ]:
                row: list = job.__repr__(ready=False)
                if row:
                    csv_writer.writerow(row)
            for job in self.__ready:
                row: list = job.__repr__(ready=True)
                if row:
                    csv_writer.writerow(row)
        logger.debug(f'A backup is saved here {path}')

    def __restore(self) -> None:
        """A stub"""
        ...
