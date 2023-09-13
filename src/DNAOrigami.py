import os.path
import re
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd


class DNAOrigami:
    """
    DNA origami contains associated staples.
    """
    __csv_df: pd.DataFrame = None  # Sequence input csv file
    csv_df_copy: pd.DataFrame = None  # copy of original csv to store assigned bases

    origami_name: str = None
    position: Tuple  # Position of the origami component in the whole design
    helix_shift: int = 0  # scaffold bases recorded from helix indexed from 0 but other design may shift this down

    def __init__(self, name: str, origami_data: Dict, csv_root: str = "") -> None:
        csv_path = os.path.join(csv_root, origami_data["path"])
        self.__csv_df = pd.read_csv(csv_path, delimiter=",")
        self.csv_df_copy = self.__csv_df.copy()

        try:
            assert len(self.__csv_df.columns) == 5  # integrity of the csv file
            test_random_sequence = self.__csv_df.loc[0, "Sequence"]
        except Exception as e:
            raise Exception(f"Error: Incorrect data in CSV file with {e}")

        if test_random_sequence == "?" * len(test_random_sequence):
            raise Exception("Error: Sequences have not been assigned for the origami design")

        try:
            # Helix shift due to the redesign of the pre-determined origami
            self.helix_shift = origami_data["shift"]

            # Load origami position information
            self.position = (origami_data["x"], origami_data["y"])
        except Exception as e:
            raise Exception(f"Error: Missing / Incorrect data in config.JSON file with {e}")

        # Name
        self.origami_name = name

        # Split the helix and base information into two columns
        _delimiter = ["[", "]"]
        self.__split_helix_base(_delimiter, "Start")
        self.__split_helix_base(_delimiter, "End")

    def __split_helix_base(self, delimiters: List[str], column_name: str):
        """
        Split helix and base indexes from column Start and End in the form of helix_idx[base_idx]
        :param delimiters: list of delimiters of column Start and End
        :param column_name: Start or End
        :return: None
        """
        # split helix and base index
        _helix_arr, _base_arr = \
            zip(*[
                re.split('|'.join(map(re.escape, delimiters)), s)[:2] for s in
                self.__csv_df.loc[:, column_name].values
            ])

        # replace helix index
        self.__csv_df[column_name] = np.array(list(map(int, _helix_arr)), dtype=np.int8)

        # insert base index column
        self.__csv_df.insert(
            1 if column_name == "Start" else 3,
            f"{column_name}_base",
            np.array(list(map(int, _base_arr)), dtype=np.int16),
            allow_duplicates=True
        )

    def get_csv_df(self) -> pd.DataFrame:
        return self.__csv_df
