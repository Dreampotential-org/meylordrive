import logging

def get_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level = logging.INFO,
        format = '[%(filename)s:%(funcName)s():line %(lineno)s] %(levelname)s: %(message)s'
    )

    return logger
