from pytest import fixture, raises, mark

from time import sleep

from logger import logger
from job import Job


# @fixture

def function_squares():
    max_ = 5
    for i in range(0, max_):
        sleep(1)
        result = i ** 2
        yield result

def test_init():
    job = Job(target=function_squares)
    id = job.get_id()
    logger.warning(f'job_id: {id}')
    job.run()
    assert isinstance(job, Job)


def test_init_wrong():
    job = Job(target=function_squares)
    assert not isinstance(job, str)
