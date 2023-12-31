from configparser import ConfigParser
from functools import partial
from multiprocessing import Process, Queue
from time import sleep
from typing import Callable, Any, Dict, Generator

from customtypes import Request, Response, ResponseStatus
from logger import logger


class Job:
    """
    A class used to represent a Job. It contains one or several tasks inside it.
    Each task should be a 'functools.partial'.
    'Partial' is like a zip with a target function and arguments together.

    Class attributes
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
                 tries: int = 0,
                 dependencies: tuple[str, ...] = tuple()):
        self.__targets = targets
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies
        self.loop: Any = None  # main coroutine of this class

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
        result = str(target())
        queue.put(result)
        logger.debug(f'Result {result} is put in the queue')

    def run(self) -> None:
        """Start a coroutine. It's being called just one time during a life of Job object."""
        self.loop = self.start_loop()

    def start_loop(self) -> Generator[Response | None, Request, None]:
        """
        Return main coroutine of the whole class.

        target is functools.partial(func, arg1, arg2 ...)
        :return: coroutine
        """
        yield None
        for i, target in enumerate(self.__targets):
            # Job do tasks one after another. Not in parallel
            queue: Queue = Queue()
            func = partial(Job.target_and_queue, target, queue)
            p = Process(target=func)
            p.start()

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

                if p.is_alive():
                    response = Response(ResponseStatus.waiting, None)
                    logger.debug(f"Job returns status '{ResponseStatus.waiting.value}'")
                    yield response
                    continue

                result = None if queue.empty() else queue.get()
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
