"""This file is for just calculation tests.
These tests don't require the internet and the file system.
"""
from configparser import ConfigParser
from datetime import datetime, timedelta
from functools import partial
from time import sleep

from pytest import fixture

from job import Job
from logger import logger
from scheduler import Scheduler

config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])


def power(a, b):
    sleep(8 * TICK)
    logger.debug(f"This is function 'power'. {a}**{b} = {a ** b}.")
    a **= b
    return a


@fixture
def fixture_for_power() -> tuple:
    tuples = ((2, 4),
              (3, 5),
              (5, 4),
              )
    return tuples


def test_calculations(fixture_for_power: tuple) -> None:
    """
    Test "three simple jobs for a scheduler"

    Parameters
    ----------
    fixture_for_power : fixture
        a fixture with variables for a power function a**b
    """
    tuples = fixture_for_power

    jobs = [Job([partial(power, *args_), ]) for args_ in tuples]
    scheduler = Scheduler()

    for job in jobs:
        assert isinstance(job, Job)
        scheduler.schedule(job)

    scheduler.run()
    scheduler.join()


def test_calculations_with_a_stop(fixture_for_power: tuple) -> None:
    """
    Test "three jobs for a scheduler with stop and rerun"

    Parameters
    ----------
    fixture_for_power : fixture
        a fixture with variables for a power function a**b
    """
    tuples = fixture_for_power

    job1 = Job([partial(power, *tuples[0])])
    scheduler = Scheduler()
    scheduler.schedule(job1)

    id1 = job1.get_id()
    job2 = Job(
        targets=[partial(power, *tuples[1])],
        start_at=str(datetime.now() + timedelta(seconds=8)),
        max_working_time=16,
        tries=6,
        dependencies=(id1,)
    )
    scheduler.schedule(job2)

    id2 = job2.get_id()
    job3 = Job(
        targets=[partial(power, *tuples[2])],
        start_at=str(datetime.now() + timedelta(seconds=16)),
        max_working_time=8,
        tries=3,
        dependencies=(id1, id2)
    )
    scheduler.schedule(job3)

    scheduler.run()
    sleep(4 * TICK)
    scheduler.stop()
    sleep(8 * TICK)
    del scheduler
    scheduler_new = Scheduler()
    scheduler_new.restart()
    sleep(TICK)
    scheduler_new.join()
