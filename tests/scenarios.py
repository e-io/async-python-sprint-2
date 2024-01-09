from configparser import ConfigParser
from functools import partial

from time import sleep

from job import Job
from scheduler import Scheduler


config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])


def schedule_jobs_sequentially(targets: list[partial]):
    """Do jobs one after another.
    This is one of basic scenarios for some tests.
    """
    scheduler = Scheduler()
    ids = []
    for target in targets:
        job = Job(
            [target],
            dependencies=(*ids,),
        )

        scheduler.schedule(job)
        ids.append(job.get_id())
    return scheduler


def run_and_wait(scheduler):
    """Simplest scenario"""
    scheduler.run()
    sleep(TICK)
    scheduler.join()


def run_stop_and_restart(scheduler):
    """Run scheduler, stop it and restart scheduler from backup"""
    scheduler.run()
    sleep(TICK)
    scheduler.stop()
    sleep(2 * TICK)
    del scheduler
    scheduler_new = Scheduler()
    scheduler_new.restart()
    scheduler_new.join()
