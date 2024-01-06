import pytest
from configparser import ConfigParser
from pathlib import Path
from pytest import fixture
from shutil import rmtree


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
    """Remove backup folder and everything inside it."""
    backup = Path('backup')
    if backup.exists():
        rmtree(backup)

@fixture()
def fixtures_for_all_tests():
    pass
