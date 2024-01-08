"""The file is for tests, required by the initial statement of work (SoW):

  - `описать конвейер выполнения основной задачи минимум из 3 задач,
     зависящих друг от друга и выполняющихся последовательно друг за другом.`
"""

from configparser import ConfigParser
from functools import partial
from pathlib import Path

from pytest import fixture

from logger import logger
from scenarios import do_jobs_sequentially

config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])
TMP = Path(config['tests']['tmp_folder'])


def job_create_dirs():
    dir1 = Path('sources')
    dir2 = Path('data/collection')
    dirs = [dir1, dir2]

    for dir_ in dirs:
        dir_path = TMP / Path(dir_)
        dir_path.mkdir(parents=True, exist_ok=True)

    return "Directories are created"


def job_create_files():
    file1 = Path('sources/hello.txt')
    file2 = Path('data/collection/newfile.txt')

    files = [file1, file2]

    for file_ in files:
        file = TMP / Path(file_)
        file.touch()

    return "Files are created"


def job_write_in_files():
    file1 = Path('sources/hello.txt')
    file2 = Path('data/collection/newfile.txt')

    files = [file1, file2]
    for file_ in files:
        file = TMP / Path(file_)
        # if file does not exist, 'r+' mode will throw an exception.
        # So, this step can't be made without previous step
        with open(file, 'r+') as opened_file:
            opened_file.write('Happy New Year 2024')

    return "Congratulations are written in every file"


def test_multi_job():
    """Test a conveyor (pipeline) of 3+ jobs"""
    target_create_dirs = partial(job_create_dirs, )
    target_create_files = partial(job_create_files, )
    target_write_in_files = partial(job_write_in_files, )
    do_jobs_sequentially((target_create_dirs, target_create_files, target_write_in_files,))
