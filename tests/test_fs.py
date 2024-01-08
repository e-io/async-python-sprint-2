"""This file is for tests, required by the initial statement of work (SoW):

  - `работа с файловой системой: создание, удаление, изменение директорий и файлов;`
  - `работа с файлами: создание, чтение, запись;`
"""

from configparser import ConfigParser
from contextlib import redirect_stdout
from functools import partial
from io import StringIO
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


def get_zen_of_python():
    string_io = StringIO()
    with redirect_stdout(string_io):
        import this
    zen_of_python = string_io.getvalue()
    return zen_of_python


@fixture
def names_of_principles():
    zen_of_python = get_zen_of_python()
    lst1 = []  # original principles
    for line in zen_of_python.split('\n')[2:8]:
        symbols = ",.*!'"
        for symbol in symbols:
            line = line.replace(symbol, '')
        lst1.append(line)

    lst2 = []  # reverted (modified) principles
    for line in lst1:
        words = line.split(' ')
        line_new = ' '.join([words[-1], *words[1:-1], words[0]])
        line_new = line_new.replace('better', 'worse').capitalize()
        lst2.append(line_new)
    return lst1, lst2


def job_fs_create_folders(names: list):
    dir_ = TMP
    dir_.mkdir(parents=False, exist_ok=True)
    for name in names:
        dir_ /= name
        dir_.mkdir(parents=False, exist_ok=True)
    return f"A chain of folders is created '{names[0]}' ... '{names[-1]}'"


def job_fs_modify_folders(names: list, names_new: list):
    dir_ = TMP
    for i, _ in enumerate(names):
        dir_old = dir_ / names[i]
        dir_new = dir_ / names_new[i]

        dir_ = dir_old.rename(dir_new)
    return f"A chain of folders is renamed '{names_new[0]}' ... '{names_new[-1]}'"


def job_fs_delete_folders(names: list):
    """Delete a chain of folders one-by-one from the end to the beginning"""
    dir_ = TMP
    for name in names:
        dir_ /= name
    while dir_ != TMP:
        dir_.rmdir()
        dir_ = dir_.parent
    return f"A chain of folders is deleted '{names[0]}' ... '{names[-1]}'"


def test_fs_directories(names_of_principles):
    job1 = Job(
        [partial(job_fs_create_folders, names_of_principles[0])],
    )

    scheduler = Scheduler(pool_size=6)
    scheduler.schedule(job1)
    id1 = job1.get_id()

    job2 = Job(
        [partial(job_fs_modify_folders, *names_of_principles)],
        dependencies=(id1,),
    )
    scheduler.schedule(job2)
    id2 = job2.get_id()

    job3 = Job(
        [partial(job_fs_delete_folders, names_of_principles[1])],
        dependencies=(id1, id2),
    )
    scheduler.schedule(job3)

    scheduler.run()

    sleep(TICK)
    scheduler.join()
    """
    scheduler.stop()
    sleep(TICK)
    scheduler.restart()
    scheduler.join()
    """


def job_fs_create_random_dirs_and_files():
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
