from enum import Enum
from dataclasses import dataclass, field


class Request(Enum):
    report_status = 'Report status'


class ResponseStatus(Enum):
    progress = 'I am in progress'
    result = 'Some results more are ready'
    # result_finish = 'Result is ready. I am finished.'
    finish = 'I am finished'


@dataclass
class Response:
    status: ResponseStatus
    new_results: dict[int, ...] = field(default_factory=lambda: {})
