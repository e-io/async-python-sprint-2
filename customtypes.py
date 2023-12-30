from enum import Enum
from dataclasses import dataclass, field


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
    new_results: dict[int, ...] = field(default_factory=lambda: {})
