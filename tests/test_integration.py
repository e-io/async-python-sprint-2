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
    sleep(TICK)
    logger.debug(f'I am "power". {a}**{b} = {a ** b}')
    a **= b
    return a


@fixture
def fixture_for_power() -> Any:
    tuples = ((2, 4),
              (3, 5),
              (5, 4),
              )
    return tuples


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

