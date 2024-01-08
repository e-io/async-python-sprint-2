"""This file is for tests, required by the initial statement of work (SoW):

  - `работа с файловой системой: создание, удаление, изменение директорий и файлов;`
  - `работа с файлами: создание, чтение, запись;`
"""

from configparser import ConfigParser
from contextlib import redirect_stdout
from functools import partial
from io import StringIO
from pathlib import Path

from pytest import fixture

from logger import logger
from scenarios import do_jobs_sequentially

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
    target_create = partial(job_fs_create_folders, names_of_principles[0])
    target_modify = partial(job_fs_modify_folders, *names_of_principles)
    target_delete = partial(job_fs_delete_folders, names_of_principles[1])

    do_jobs_sequentially([target_create, target_modify, target_delete])


def job_fs_create_files(names, strings):
    dir_ = TMP
    for i, name in enumerate(names):
        string_ = strings[i]

        path = dir_ / (name + '.txt')
        with open(path, 'w+') as file:
            file.write(string_)

    return f"{len(names)} files were created and different lines were written in each of them"


def job_fs_modify_files(names, strings_new):
    dir_ = TMP
    for i, name in enumerate(names):
        string_new = strings_new[i]

        path = dir_ / (name + '.txt')
        if not path.exists():
            raise Exception(f"file {path} does not exist")
        with open(path, 'w+') as file:
            file.write(string_new)

    return f"Content of {len(names)} files was re-written with the new content"


def job_fs_read_files(names):
    dir_ = TMP
    last_words = []
    for name in names:
        path = dir_ / (name + '.txt')
        if not path.exists():
            raise Exception(f"file {path} does not exist")
        with open(path, 'r') as file:
            last_words.append(file.read().split(' ')[-1])

    return 'Last words in every file: ' + '; '.join(last_words)


def test_fs_files(names_of_principles):
    target_create = partial(job_fs_create_files, names_of_principles[0], names_of_principles[0])
    target_modify = partial(job_fs_modify_files, names_of_principles[0], names_of_principles[1])
    target_read = partial(job_fs_read_files, names_of_principles[0])

    do_jobs_sequentially((target_create, target_modify, target_read,))


def job_fs_random_dirs():
    dir1 = Path('sources')
    dir2 = Path('data/collection')
    dirs = [dir1, dir2]

    for dir_ in dirs:
        dir_path = TMP / Path(dir_)
        dir_path.mkdir(parents=True, exist_ok=True)

    return "Directories are created"


def job_fs_random_files():
    file1 = Path('sources/hello.txt')
    file2 = Path('data/collection/newfile.txt')

    files = [file1, file2]

    for file_ in files:
        file = TMP / Path(file_)
        with open(file, 'w+') as opened_file:
            opened_file.write('Happy New Year 2024')

    return "Files are created"


def test_fs_create_random_dirs_and_files():
    target_dirs = partial(job_fs_random_dirs, )
    target_files = partial(job_fs_random_files, )
    do_jobs_sequentially((target_dirs, target_files,))
