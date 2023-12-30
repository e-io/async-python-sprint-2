import logging


def get_custom_logger():
    """Default logger for all files in this project"""

    formatter = logging.Formatter('%(levelname)s-%(filename)s-%(lineno)d: %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    __logger = logging.getLogger('Default')
    __logger.setLevel(level='DEBUG')
    __logger.addHandler(handler)

    return __logger


logger = get_custom_logger()
