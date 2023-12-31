import logging


def get_custom_logger():
    """Return default logger for all files in this project."""

    formatter = logging.Formatter('%(levelname)s-%(filename)s-%(funcName)s-%(lineno)d:\t%(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    __logger = logging.getLogger('Default')
    __logger.setLevel(level='DEBUG')
    __logger.addHandler(handler)

    return __logger


logger = get_custom_logger()
