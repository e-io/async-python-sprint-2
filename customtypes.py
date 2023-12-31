from enum import Enum
from dataclasses import dataclass, field

from typing import Any


class Request(Enum):
    """A class used to represent signals from class Scheduler to class Job."""
    report_status = 'Report status'


class ResponseStatus(Enum):
    """A class used to represent **kinds of signals** from class Job to class Scheduler."""
    # depend
    # timeout
    waiting = 'Task is in progress. Results are waiting.'  # former 'progress'
    error = 'Exception is caught'
    result = 'A result of one task is ready.'
    finish = 'All tasks of this specific job are finished.'


@dataclass
class Response:
    """A class used to represent **signals** from class Job to class Scheduler.

    Attributes
    status: ResponseStatus
        type of signal (type of response)
    new_results : None | dict[int, Any]
        just an optional attribute.
    """
    status: ResponseStatus
    new_results: None | dict[int, Any] = field(default_factory=lambda: {})
