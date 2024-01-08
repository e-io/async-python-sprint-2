from ast import literal_eval
from configparser import ConfigParser
from csv import (
    writer as Csv_writer,
    DictReader
)
import json
import pickle
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
        backup_path = str(config['scheduler']['backup'])

        self.queue: Queue = Queue()
        self.scheduler = _Scheduler(queue=self.queue, pool_size=pool_size, tick=self.__tick, backup=backup_path)
        self.process = Process(target=self.scheduler.run,)

    def schedule(self, job: Job) -> None:
        """Add a job in the list of pending jobs."""
        self.scheduler.schedule(job)

    def run(self) -> None:
        """Start a process with real _Scheduler.
        It's recommended to use join() (or sleep()) after run() in your function
        """
        self.process.start()

    def join(self) -> None:
        self.process.join()

    def stop(self) -> None:
        logger.debug("Scheduler.stop is called")
        self.queue.put('stop')
        sleep(self.__tick)
        self.clear()

    def clear(self) -> None:
        del self.scheduler
        del self.process
        del self.queue

    def restart(self) -> None:
        scheduler = self.scheduler
        self.queue = Queue()
        self.scheduler.queue = self.queue
        self.process = Process(target=scheduler.restart,)
        self.process.start()


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
    def __init__(self, queue: Queue, pool_size: int, tick: float, backup: str) -> None:
        self.__pool_size: int = pool_size
        self.__pending: list[Job] = []
        self.__pool: list[Job] = []
        self.__ready: list[Job] = []
        self.__tick: float = tick
        self.backup_path: Path = Path(backup)
        self.queue = queue

    def schedule(self, job: Job) -> None:
        """Add a job in the list of pending jobs."""
        self.__pending.append(job)

    def run(self) -> None:
        self.__run()

    def __run(self) -> None:
        """Do jobs. This is the main loop of the whole class."""
        while True:
            sleep(self.__tick)
            logger.debug("The first line of main 'while' cycle of Scheduler.")

            if not self.queue.empty():
                message = self.queue.get()
                if message == 'stop':
                    self.stop()
                    break

            self._move_from_pending_to_pool()

            if not self.__pool:
                break  # no job anymore

            finished: list[int] = []  # indices of finished jobs
            for (i, job) in enumerate(self.__pool):
                is_finished = self._handle_1_job(job)

                if is_finished:
                    finished.append(i)

            for i in finished:
                job = self.__pool[i]
                self.__ready.append(job)
            for i in finished[::-1]:
                self.__pool.pop(i)

        logger.debug(f"Scheduler finished its work. "
                     f"Finished jobs: {len(self.__ready)}")

    def _move_from_pending_to_pool(self):
        space = self.__pool_size - len(self.__pool)  # must be >=0

        for _ in range(space):
            if not self.__pending:  # not targets anymore
                return
            job = self.__pending.pop(0)
            job.run()
            logger.debug(f"Initial calling of 'next' for a job with id '{job.get_id()}'")
            next(job.loop)
            self.__pool.append(job)

    def _handle_1_job(self, job: Job) -> bool:
        """Handle 1 job for one time. If job is finished, return True. If not - return False."""
        sleep(self.__tick / 4)
        if not self.queue.empty():
            message = self.queue.get()
            self.queue.put(message)
            if message == 'stop':
                return False
            else:
                pass  # just ignore

        logger.debug(f"A call of 'next' for {job.get_id()}")
        next(job.loop)
        logger.debug(f"Sending request to {job.get_id()}")
        response: Response = job.loop.send(Request.report_status)
        logger.debug(f"Scheduler got response '{response.status.value}'")

        if response.status is ResponseStatus.waiting:
            return False
        if response.status is ResponseStatus.result:
            logger.debug(f"Scheduler got result  '{response.new_results}' from {job.get_id()}")
            return False
        if response.status is ResponseStatus.error:
            logger.debug(f"{job.get_id()} informed Scheduler about an exception '{response.new_results}'")
            return False
        if response.status is ResponseStatus.finish:
            return True
        return False

    def stop(self) -> None:
        """Stop all jobs and backup their condition."""
        logger.debug("This is _Scheduler.stop()")
        self.__backup()
        exit(0)

    def __backup(self) -> None:
        """Save the state of all "jobs" in a CSV file"""
        logger.debug("This is '__backup' method'")

        spreadsheet_extension = '.tsv'

        path = self.backup_path
        if path.suffix != spreadsheet_extension:
            path = path.with_suffix(spreadsheet_extension)
        logger.debug(f'A backup will be saved in the file {path}')
        if path.parent:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w+') as csv_:  # spreadsheet
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

            def write_row(job: Job, is_ready: bool):
                row: list = job.list_repr(is_ready=is_ready)
                if row:
                    csv_writer.writerow(row)

            # this is the most correct order for the correct restore later
            for job in [*self.__pool, *self.__pending, ]:
                write_row(job, False)
            for job in self.__ready:
                write_row(job, False)
        logger.debug(f'A backup is saved here: {path}')

        path = path.with_suffix('.json')
        with open(path, 'w+') as json_:
            data = {
                'pool_size': self.__pool_size,
            }
            json_.write(json.dumps(data))
        logger.debug(f'Additional backup json file is saved here: {path}')
        sleep(10 * self.__tick)  # just wait for while
        self.__clear()

    def __clear(self) -> None:
        """Just prevent usage of _Scheduler object if it was stopped"""
        del self.__pool
        del self.__pending
        del self.__ready
        del self.__pool_size
        del Job.all_id

    def restart(self) -> None:
        """Start all jobs again where they were stopped."""
        logger.debug("This is a call of restart method")
        self.__restore()
        self.__run()

    def __restore(self) -> None:
        """Restore all jobs using backup file."""
        logger.debug("This is a call of __restore method")
        path = self.backup_path

        path = path.with_suffix('.json')
        if not path.exists():
            # logger.debug(path)
            # logger.debug(Path('.').resolve())
            raise Exception('Backup (.json) does not exist. So, it is impossible to restore Scheduler.')
        with open(path, 'r') as json_:
            dict_ = json.load(json_)
            self.__pool_size = dict_["pool_size"]

        path = path.with_suffix('.tsv')
        if not path.exists():
            raise Exception('Backup does not exist. So, it is impossible to restore jobs.')
        with open(path, 'r') as tsv:
            dict_reader = DictReader(tsv, delimiter='\t')

            for row in dict_reader:
                if row['status'] != 'PROGRESS':
                    continue

                func = pickle.loads(literal_eval(row['pickled']))

                start_at = row['start_at']
                dependencies = literal_eval(row['dependencies'])

                if start_at == 'ASAP':
                    start_at = ''
                job = Job(targets=[func,],
                          start_at=start_at,
                          max_working_time=int(row['max_working_time']),
                          tries=int(row['tries_left']),
                          dependencies=dependencies,
                          id=row['job_id'],
                          )

                self.schedule(job)

                is_ready = True if row['status'] == 'READY' else False
                logger.debug(f"Next job is scheduled: {job.list_repr(is_ready)[:-1]}")
        logger.debug(f"Scheduler is restored. It contains {len(self.__pending)} jobs.")
