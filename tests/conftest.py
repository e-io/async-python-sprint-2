"""Actions before every run of all tests."""

from configparser import ConfigParser
from pathlib import Path
from shutil import rmtree


config = ConfigParser()
config.read('setup.cfg')
TMP = Path(config['tests']['tmp_folder'])
BACKUP = Path(config['scheduler']['backup'])


def test_actions_before_all_tests():
    """Remove `backup` and `tmp` folders and everything inside them.
    Then, create `tmp` folder (it's needed for tests only).
    """
    backup_parent = BACKUP.parent
    if backup_parent and backup_parent.exists():
        rmtree(backup_parent)
    tmp = TMP
    if tmp.exists():
        rmtree(tmp)
    tmp.mkdir()
