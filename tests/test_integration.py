"""
The main file for tests.
"""

from configparser import ConfigParser
from functools import partial
from time import sleep
from typing import Any

from pytest import fixture

from job import Job
from logger import logger
from scheduler import Scheduler

config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])


def power(a, b):
    sleep(10*TICK)
    logger.debug(f"This is function 'power'. {a}**{b} = {a ** b}")
    a **= b
    return a


@fixture
def fixture_for_power() -> Any:
    tuples = ((2, 4),
              (3, 5),
              (5, 4),
              )
    return tuples


def test_3jobs(fixture_for_power: tuple) -> None:
    """
    Test "three jobs for one scheduler"

    Parameters
    ----------
    fixture_for_power : fixture
        a fixture with variables for power function a**b
    """
    tuples = fixture_for_power

    jobs = [Job([partial(power, *args_), ]) for args_ in tuples]
    scheduler = Scheduler()

    for job in jobs:
        assert isinstance(job, Job)
        scheduler.schedule(job)

    scheduler.run()


def test_a_stop(fixture_for_power: tuple) -> None:
    """
    Test "three jobs for one scheduler"

    Parameters
    ----------
    fixture_for_power : fixture
        a fixture with variables for power function a**b
    """
    tuples = fixture_for_power

    jobs = [Job([partial(power, *args_)]) for args_ in tuples]
    scheduler = Scheduler()

    for job in jobs:
        scheduler.schedule(job)

    scheduler.run()
    sleep(3*TICK)
    scheduler.stop()


def test_3tasks_in_1job(fixture_for_power: tuple):
    tuples = fixture_for_power

    job_3tasks = Job([partial(power, *args_) for args_ in tuples])
    scheduler = Scheduler()

    scheduler.schedule(job_3tasks)

    args = [i + 1 for i in tuples[0]]
    job_1task = Job([partial(power, *args)])

    scheduler.schedule(job_1task)

    scheduler.run()


def web_job():
    ...


def fs_job():
    ...


def multi_job():
    ...
