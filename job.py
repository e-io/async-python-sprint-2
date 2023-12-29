from configparser import ConfigParser
from multiprocessing import Process, Queue
from typing import Callable
from functools import partial

from logger import logger
from customtypes import Request, Response, ResponseStatus


from functools import wraps


def coroutine(f):
    @wraps(f)  # https://docs.python.org/3/library/functools.html#functools.wraps
    def wrap(*args, **kwargs):
        gen = f(*args, **kwargs)
        gen.send(None)
        return gen
    return wrap


class Job:
    all_id: {str: int} = {}  # str: int

    config = ConfigParser()
    config.read('setup.cfg')
    __max_id_length = float(config['job']['max_id_length'])

    def __init__(self, targets: [partial],
                 start_at: str = "",
                 max_working_time: int = -1,
                 tries: int = 0,
                 dependencies: [str] = []):
        self.__targets = targets
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies

        name = ''
        for target in targets:
            name += target.func.__name__
            if len(name) > Job.__max_id_length:
                break

        if name in Job.all_id.keys():
            Job.all_id[name] += 1
        else:
            Job.all_id[name] = 1
        self.__id = name + '_' + str(Job.all_id[name])

    def get_id(self):
        return self.__id

    def run(self):
        ...

    @staticmethod
    def target_and_queue(target: Callable, queue: Queue):
        result = str(target())
        queue.put(result)

    def loop(self) -> None:
        yield None
        for i, target in enumerate(self.__targets):

            queue = Queue()
            p = Process(target=Job.target_and_queue, args=(target, queue))
            p.start()
            while True:
                request: Request = yield

                if request is Request.report_status:
                    if p.is_alive():
                        response: Response = Response(ResponseStatus.progress, None)
                        yield response
                        continue

                    result = queue.get() if queue else None
                    response: Response = Response(ResponseStatus.result, {i: result})
                    logger.debug(f"{self.__id}: {result}")
                    yield response
                    break

        response = Response(ResponseStatus.finish, None)
        yield response

    def pause(self):
        pass

    def stop(self):
        pass
