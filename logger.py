import logging


def get_custom_logger():
    """Default logger for all files in this project"""

    formatter = logging.Formatter('%(levelname)s-%(filename)s-%(lineno)d: %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger('Default')
    logger.setLevel(level='DEBUG')
    logger.addHandler(handler)

    return logger


logger = get_custom_logger()
