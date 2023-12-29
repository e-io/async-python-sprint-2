from functools import partial
from time import sleep

from pytest import fixture

from job import Job
from logger import logger
from scheduler import Scheduler

@fixture
def fixture_default():
    def power(a, b):
        sleep(1)
        a **= b
        return a
    a = 9
    b = 11
    return power, a, b


def test_2jobs(fixture_default: tuple):
    power, a, b = fixture_default

    job1 = Job(targets=[partial(power, a, b),])
    job2 = Job(targets=[partial(power, a, b),])
    scheduler = Scheduler()

    for job in (job1, job2):
        scheduler.schedule(job)

    scheduler.run()
