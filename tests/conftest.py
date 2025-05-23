import logging

disable_loggers = [
    "matplotlib",
    "PIL",
    "msoffcrypto",
]


def pytest_configure():
    for logger_name in disable_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
