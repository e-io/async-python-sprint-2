from functools import partial
from time import sleep

from job import Job
from scheduler import Scheduler

from pytest import fixture


@fixture
def fixture_default():
    def power(a, b):
        sleep(1)
        a **= b
        return a
    a = 9
    b = 11
    return power, a, b


def test_2jobs(power, a, b):
    job1 = Job(targets=[partial(power, a, b),])
    job2 = Job(targets=[partial(power, a, b),])
    scheduler = Scheduler()
    for job in (job1, job2):
        scheduler.schedule(job)

    scheduler.run()
