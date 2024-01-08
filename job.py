from configparser import ConfigParser
from functools import partial
from multiprocessing import Process, Queue
from pickle import dumps as pickle_dumps
from time import sleep
from typing import Callable, Any, Dict, Generator, Optional

from customtypes import Request, Response, ResponseStatus, EXCEPTION
from logger import logger


class Job:
    """
    A class used to represent a Job. It contains one or several tasks inside it.
    Each task should be a 'functools.partial'.
    'Partial' is like a zip with a target function and arguments together.

    Attributes
    ----------
    all_id : dict
        contains already used identifiers and their total number
    __max_id_length : int
        the max length of identifier (also 2 digits will be added like '_01').
    __tick : float
        something like 'a frequency' of the whole project in seconds
    """
    all_id: Dict[str, int] = {}

    config = ConfigParser()
    config.read('setup.cfg')
    __max_id_length = float(config['job']['max_id_length'])
    __tick = float(config['scheduler']['tick'])

    def __init__(self, targets: list[partial],
                 start_at: str = "",
                 max_working_time: int = -1,
                 tries: int = 1,
                 dependencies: tuple[str, ...] = tuple(),
                 id: Optional[str] = None):  # id should be set externally just in case of restoring from backup
        self.__targets = targets
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies
        self.loop: Any = None  # main coroutine of this class

        if id:   # id should be set from outside just in case of restoring from backup
            self.__id = id
            return

        name = ''
        for target in targets:
            name += target.func.__name__
            if len(name) > Job.__max_id_length:
                break

        if name in Job.all_id.keys():
            Job.all_id[name] += 1
        else:
            Job.all_id[name] = 1
        logger.debug(f"all_id dictionary: {Job.all_id}")

        siblings = Job.all_id[name]  # other jobs which have the same basic name
        zero = '0' if siblings < 10 else ''
        self.__id = name + '_' + zero + str(siblings)

    def get_id(self) -> str:
        """Return identifier of a Job."""
        return self.__id

    @staticmethod
    def target_and_queue(target: Callable, queue: Queue) -> None:
        """Wrap a function into another function and put a result in a queue."""
        try:
            result = str(target())
        except Exception as e:
            logger.warning(f'Exception is caught {e}')
            queue.put(EXCEPTION + str(e))
        else:
            queue.put(result)
            logger.debug(f'Result {result} is put in the queue')

    def run(self) -> None:
        """Start a coroutine. It's being called just one time during a life of Job object."""
        self.loop = self.start_loop()

    def start_loop(self) -> Generator[Response | None, Request, None]:
        """
        Return main coroutine of the whole class.

        target is functools.partial(func, arg1, arg2 ...)

        Returns
        -------
        coroutine
            a coroutine.
        """
        yield None
        for i, target in enumerate(self.__targets):
            # Job do tasks one after another. Not in parallel
            queue: Queue = Queue()
            func = partial(Job.target_and_queue, target, queue)
            process = Process(target=func)
            process.start()

            while True:
                request = yield None
                logger.debug(f"Job got request '{request.value}'")
                sleep(3 * Job.__tick)

                response: None | Response = None
                if request != Request.report_status:
                    response = Response(ResponseStatus.error, None)
                    logger.debug("Unknown type of request")
                    yield response
                    continue

                if process.is_alive():
                    response = Response(ResponseStatus.waiting, None)
                    logger.debug(f"Job returns status '{ResponseStatus.waiting.value}'")
                    yield response
                    continue

                result = None if queue.empty() else queue.get()
                if result and result.startswith(EXCEPTION):
                    result = result[len(EXCEPTION):]
                    logger.debug(f'Exception {result} is taken from the queue')
                    response = Response(ResponseStatus.error, {i: result})
                else:
                    logger.debug(f'{self.__id}: Result {result} is taken from the queue')
                    response = Response(ResponseStatus.result, {i: result})
                yield response
                break
        yield None
        response = Response(ResponseStatus.finish, None)
        yield response

    def pause(self) -> None:
        """Pause a job."""
        ...

    def stop(self) -> None:
        """Stop a job."""
        ...

    def list_repr(self, is_ready: bool = True) -> list[str]:
        """return representation of a job for writing in CSV spreadsheet.
        Order is according to 'header' in 'scheduler'.
        This is like __repr__, but it returns a list, not str.
        """
        # the same 'PROGRESS' status for all cases except for 'READY' status
        status = 'READY' if is_ready else 'PROGRESS'
        # func = 'pickled stub',
        func = pickle_dumps(self.__targets[0])
        row = [self.__id,
               status,
               self.start_at if self.start_at else 'ASAP',
               self.max_working_time,
               self.tries,  # it should contain only tries left
               self.dependencies,
               func,
               ]
        row_of_str = []
        for item in row:
            token = str(item)
            token.replace('\t', '    ')
            row_of_str.append(token if token else 'ERROR')
        return row_of_str
