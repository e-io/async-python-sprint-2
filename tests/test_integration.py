from functools import partial
from time import sleep

from pytest import fixture

from job import Job
from logger import logger
from scheduler import Scheduler

@fixture
def fixture_for_power():
    tuple_ = ((2, 4),
              (3, 5),
              )

    return tuple_

def power(a, b):
    sleep(1)
    logger.debug(f'I am "power". {a}**{b} = {a ** b}')
    a **= b
    return a


def test_2jobs(fixture_for_power: tuple):
    tuples = fixture_for_power

    jobs = [Job([partial(power, *args_)]) for args_ in tuples]
    scheduler = Scheduler()

    for job in jobs:
        scheduler.schedule(job)

    scheduler.run()


def web_job():
    ...


def fs_job():
    ...


def multi_job():
    ...

