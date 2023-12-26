from job import Job
from scheduler import Scheduler

from pytest import fixture


@fixture
def fixture_default():
    scheduler = Scheduler()
    job = Job(target=None)

