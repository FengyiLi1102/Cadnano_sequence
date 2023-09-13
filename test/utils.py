import argparse
import logging

from src.DNAOrigami import DNAOrigami
from rich.logging import RichHandler


def csv_loader(path: str) -> DNAOrigami:
    """
    ONLY FOR TESTS
    :param path: csv file path
    :return: DNA origami
    """
    data = {
        "path": path,
        "x": 0,
        "y": 0,
        "shift": 0
    }

    # Initialise the origami
    return DNAOrigami("test", data)


def args_generator(path):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-cp",
                        type=str,
                        default=path)
    return parser.parse_args()
