from scheduler import Scheduler


def test_init():
    scheduler = Scheduler()
    assert isinstance(scheduler, Scheduler)
