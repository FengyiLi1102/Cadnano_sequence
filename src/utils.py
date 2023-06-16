import logging

from rich.logging import RichHandler


def config_logging():
    """
    Set the logging format.
    :return: None
    """
    FORMAT = "%(message)s"
    logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])
