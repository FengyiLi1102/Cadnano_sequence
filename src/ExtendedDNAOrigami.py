from __future__ import annotations

import argparse
import json
from typing import Tuple, Dict

from src.DNAOrigami import DNAOrigami

import logging

from test.utils import config_logging

config_logging()  # logging configuration set-up
logger = logging.getLogger(__name__)


class ExtendedDNAOrigami:
    """
    Designed whole structure containing multiple origami.
    """
    __size: Tuple  # Dimension of the design
    __color_setting: Dict[str, str]  # color setting for all staples
    __origami_position_dict: Dict[Tuple[int, int], DNAOrigami] = dict()  # each origami chip and its position
    __csv_root_path: str  # root path of csv files for each origami in design

    @classmethod
    def load_design(cls, args: argparse.Namespace) -> ExtendedDNAOrigami:
        """
        Factory method to load data from the configuration file.
        :param args: argument namespace containing configuration file and csv file root path, saving file name
        :return: cls()
        """
        ext_dns_ori = cls()

        # Load configuration file
        origami_data = ext_dns_ori.__load_configuration(args.config)

        for name, data in origami_data.items():
            temp_origami = DNAOrigami(name, data, ext_dns_ori.__csv_root_path)
            ext_dns_ori.__origami_position_dict[temp_origami.position] = temp_origami

        return ext_dns_ori

    def __load_configuration(self, config_path: str) -> Dict[str, Dict]:
        """
        Load configuration file and save required data in the class-level attributes.
        :param config_path: configuration file path
        :return: dict of DNA origami components containing component name and DNA origami objects
        """
        with open(config_path, "r") as f:
            config_data = json.load(f)

            # Sanity check
            if len(config_data["DNA_origami"]) != int(config_data["size_x"] * config_data["size_y"]):
                raise Exception("Error: Number of origami is incorrect.")

        try:
            self.__size = (config_data["size_x"], config_data["size_y"])
            self.__color_setting = config_data["colors"]
            self.__csv_root_path = config_data["csv_root_path"]
            assert config_data["DNA_origami"] is not None
        except Exception as e:
            raise Exception(f"Error: Incorrect data in JSON with {e}")

        return config_data["DNA_origami"]

    def get_color_setting(self) -> Dict[str, str]:
        return self.__color_setting

    def get_size(self) -> Tuple:
        return self.__size

    def get_origami_position(self) -> Dict[Tuple[int, int], DNAOrigami]:
        return self.__origami_position_dict
