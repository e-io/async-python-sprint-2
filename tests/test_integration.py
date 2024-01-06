"""This file is for testing during development process"""

from configparser import ConfigParser
from datetime import datetime, timedelta
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
    scheduler.join()


def test_a_stop(fixture_for_power: tuple) -> None:
    """
    Test "three jobs for one scheduler"

    Parameters
    ----------
    fixture_for_power : fixture
        a fixture with variables for power function a**b
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
    sleep(3*TICK)
    scheduler.stop()
    sleep(8*TICK)
    del scheduler
    scheduler_new = Scheduler()
    scheduler_new.restart()
    sleep(TICK)
    scheduler_new.join()


def test_3tasks_in_1job(fixture_for_power: tuple):
    tuples = fixture_for_power

    job_3tasks = Job([partial(power, *args_) for args_ in tuples])
    scheduler = Scheduler()

    scheduler.schedule(job_3tasks)

    args = [i + 1 for i in tuples[0]]
    job_1task = Job([partial(power, *args)])

    scheduler.schedule(job_1task)

    scheduler.run()
