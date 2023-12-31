from functools import partial
from random import randint

from pytest import fixture

from job import Job
from logger import logger


def square(a):
    a **= 2
    return a


@fixture
def fixture_for_square() -> int:
    return randint(-10, 10)


def test_correct_id(fixture_for_square) -> None:
    job = Job(targets=[partial(square, fixture_for_square)])
    id_ = job.get_id()
    logger.debug(f"Job with job_id: '{id_}' is created.")
    assert id_ == 'square' + '_01'


def test_isinstance(fixture_for_square) -> None:
    job = Job(targets=[partial(square, fixture_for_square)])
    assert isinstance(job, Job)
    assert not isinstance(job, str)
