from __future__ import annotations

from collections import defaultdict
from typing import List, Dict, Tuple

import pandas as pd


class Staple:
    """
    Staples strengthen the scaffolds or work as overhangs to connect other origami.
    """
    __start_helix_idx: int = None
    __start_base_idx: int = None
    __end_helix_idx: int = None
    __end_base_idx: int = None

    __sequences: List[str] = None
    __color: str = None

    # Related to overhangs
    is_overhang: bool = False
    __location: str = None

    def __init__(self, staple_info: pd.Series, color_setting: Dict[str, str]) -> None:
        """
        Initialisation method.
        :param staple_info: Row in csv file
        :param color_setting: color for different staples such as overhangs, pre-determined staples.
        :param origami_name: position of origami in the whole design
        """
        if len(staple_info) != 7:
            raise Exception("Error: Failed to process staples on the origami.")

        try:
            self.__start_helix_idx = staple_info["Start"]
            self.__start_base_idx = staple_info["Start_base"]
            self.__end_helix_idx = staple_info["End"]
            self.__end_base_idx = staple_info["End_base"]
            self.__sequences = list(staple_info["Sequence"])
            self.__color = staple_info["Color"]
        except Exception as e:
            raise Exception(f"Error: Incorrect data for creating a staple {e}.")

        # Locate staples on the origami in the direction of left, right, top or bottom
        if self.__color == color_setting["side_overhang"]:
            # Side staples
            if self.__start_base_idx > 200:
                self.__location = "r"  # right
            else:
                self.__location = "l"
        elif self.__color == color_setting["other_overhang"]:
            # Bottom or top staples
            if self.__start_helix_idx > 15:
                self.__location = "b"  # bottom
            else:
                self.__location = "t"
        elif self.__color == color_setting["modified_staples"]:
            # modified inactive staples
            self.__location = "modified"
        else:
            self.__location = "normal"

        # End processing if the staple is a normal staple
        if "?" in list(self.__sequences) and \
                self.__color in [color_setting["side_overhang"], color_setting["other_overhang"]]:
            self.is_overhang = True

    @staticmethod
    def extract_staples_sequences(staple_list: List[Staple]) -> List[str]:
        """
        Create a list of sequences from provided staples.
        :param staple_list: list of staples
        :return: list of sequence strings
        """
        return ["".join(staple.get_sequence()) for staple in staple_list]

    def __str__(self):
        """
        Human-readable information of the staple.
        :return:
        """
        space = " " * 3
        return "{0:<2}[{1:<3}]{2}{3:<2}[{4:<3}]{5}{6}".format(self.__start_helix_idx, self.__start_base_idx, space,
                                                              self.__end_helix_idx, self.__end_base_idx, space,
                                                              self.__sequences)

    @staticmethod
    def read_staple_data(staples_list: List[Staple]) -> dict:
        """
        Convert split helix and base indexes back to the original format helix_index[base_index].
        :param staples_list: list of staples provided
        :return: dict in the form of csv file
        """
        staples_data_dict = defaultdict(list)

        for staple in staples_list:
            start = str(staple.get_helix_index()[0]) + "[" + str(staple.get_base_index()[0]) + "]"
            end = str(staple.get_helix_index()[1]) + "[" + str(staple.get_base_index()[1]) + "]"
            staples_data_dict["Start"].append(start)
            staples_data_dict["End"].append(end)
            staples_data_dict["Sequence"].append("".join(staple.get_sequence()))
            staples_data_dict["Length"].append(len(staple.get_sequence()))
            staples_data_dict["Color"].append(staple.get_color())

        return staples_data_dict

    def get_sequence(self) -> List:
        return self.__sequences

    def get_position(self) -> str:
        return self.__location

    def get_base_index(self) -> Tuple:
        return self.__start_base_idx, self.__end_base_idx

    def get_helix_index(self) -> Tuple:
        return self.__start_helix_idx, self.__end_helix_idx

    def get_color(self) -> str:
        return self.__color

    def set_sequence(self, sequence: str) -> None:
        self.__sequences = list(sequence)
