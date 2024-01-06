from shutil import rmtree
from pathlib import Path
from pytest import fixture


@fixture()
def fixtures_for_all_tests():
    pass


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
