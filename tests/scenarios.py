from configparser import ConfigParser
from functools import partial

from time import sleep

from job import Job
from logger import logger
from scheduler import Scheduler


config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])


def do_jobs_sequentially(targets: list[partial]):
    scheduler = Scheduler(pool_size=9)
    ids = []
    for target in targets:
        job = Job(
            [target],
            dependencies=(*ids,),
        )

        scheduler.schedule(job)
        ids.append(job.get_id)

    scheduler.run()
    sleep(TICK)
    scheduler.join()

    """
    scheduler.stop()
    sleep(TICK)
    scheduler.restart()
    scheduler.join()
    """