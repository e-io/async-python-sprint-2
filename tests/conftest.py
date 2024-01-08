import pytest
from configparser import ConfigParser
from pathlib import Path
from pytest import fixture
from shutil import rmtree


config = ConfigParser()
config.read('setup.cfg')
TICK = float(config['scheduler']['tick'])
TMP = Path(config['tests']['tmp_folder'])
BACKUP = Path(config['scheduler']['backup'])

def pytest_configure():  # does not work
    config = ConfigParser()
    config.read('setup.cfg')

    pytest.TICK = float(config['scheduler']['tick'])
    pytest.TMP = Path(config['tests']['tmp_folder'])


@fixture
def fixture_for_power() -> tuple:
    tuples = ((2, 4),
              (3, 5),
              (5, 4),
              )
    return tuples


def test_actions_before_all_tests():
    """Remove backup and tmp folder and everything inside them.
    Then, create tmp folder (it's needed for tests only)."""
    backup_parent = BACKUP.parent
    if backup_parent and backup_parent.exists():
        rmtree(backup_parent)
    tmp = TMP
    if tmp.exists():
        rmtree(tmp)
    tmp.mkdir()


@fixture()
def fixtures_for_all_tests():
    pass
