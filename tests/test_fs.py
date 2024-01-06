"""This file is for tests, required by the initial statement of work (SoW):

  - `работа с файловой системой: создание, удаление, изменение директорий и файлов;`
  - `работа с файлами: создание, чтение, запись;`
"""

from configparser import ConfigParser
from functools import partial
from pathlib import Path
from time import sleep

from pytest import fixture

from job import Job
from logger import logger
from scheduler import Scheduler

config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])
TMP = Path(config['tests']['tmp_folder'])


def job_fs_step_create():
    dir1 = Path('sources')
    dir2 = Path('data/collection')
    file1 = Path('data/collection/newfile.txt')

    dirs = [dir1, dir2]
    files = [file1, ]

    for file in files:
        dirs.append(file.parent)

    for dir_ in dirs:
        dir = TMP / Path(dir_)
        dir.mkdir(parents=True, exist_ok=True)

    for file_ in files:
        file = TMP/ Path(file_)
        with open(file, 'w+') as opened_file:
            opened_file.write('Happy New Year 2024')

    sleep(2 * TICK)

    return "Directories are created"


def job_fs_step_delete():
    dir1 = Path('sources')
    dir2 = Path('data/collection')
    file1 = Path('data/collection/newfile.txt')

    dirs = [dir1, dir2]
    files = [file1, ]


    for file_ in files:
        file = TMP/ Path(file_)
        file.unlink()

    for dir_ in dirs:
        dir = TMP / Path(dir_)
        dir.rmdir()

    return "Directories are removed"


def test_fs():
    job1 = Job(
        [partial(job_fs_step_create)],
    )

    scheduler = Scheduler()
    scheduler.schedule(job1)
    id1 = job1.get_id()
    job2 = Job(
        [partial(job_fs_step_delete)],
        dependencies=(id1,),
    )
    scheduler.schedule(job2)

    scheduler.run()
    sleep(TICK)
    scheduler.join()
    """
    scheduler.stop()
    sleep(TICK)
    scheduler.restart()
    scheduler.join()
    """
