from enum import Enum
from dataclasses import dataclass, field

from typing import Any


class Request(Enum):
    report_status = 'Report status'


class ResponseStatus(Enum):
    # depend
    # timeout
    waiting = 'Task is in progress. Results are waiting.'  # former 'progress'
    error = 'Exception is caught'
    result = 'A result of one task is ready.'
    finish = 'All tasks (>=1) are finished.'


@dataclass
class Response:
    status: ResponseStatus
    new_results: None | dict[int, Any] = field(default_factory=lambda: {})
