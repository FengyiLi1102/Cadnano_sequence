import argparse
import re

import numpy as np
import pandas as pd
from src.constants import GREEN, CYAN, PURPLE, BLACK


class Reader:
    # Sequence input csv file
    sequence_arr: pd.DataFrame = None

    def __init__(self, args: argparse.Namespace) -> None:
        self.sequence_arr = pd.read_csv(args.input_path, delimiter=",")

        # Check whether the sequences have been assigned to the design
        test_random_sequence = self.sequence_arr.loc[0, "Sequence"]
        if test_random_sequence == "?" * len(test_random_sequence):
            raise Exception("Error: Sequences have not been assigned for the origami design")

        """
        Check if the correct colors are used to represent staples
        Green  : data bit
        Cyan   : Bottom / Top overhangs
        Purple : Left / Right side overhangs
        Black  : Staples between scaffolds
        Aqua   : Scaffolds
        """
        if set(self.sequence_arr["Color"].unique()) != {GREEN, CYAN, PURPLE, BLACK}:
            raise Exception("Error: Color standards are not followed")

        # Split the base and corresponding helix at start and end points for staples
        # Helix[base] -> Helix, base
        delimiters = ["[", "]"]
        self.split_helix_base(delimiters, "Start")
        self.split_helix_base(delimiters, "End")

    def split_helix_base(self, delimiters, position):
        _helix_arr, _base_arr = \
            zip(*[
                re.split('|'.join(map(re.escape, delimiters)), s)[:2] for s in self.sequence_arr.loc[:, position].values
            ])
        self.sequence_arr.loc[:, position] = np.array(list(map(int, _helix_arr)), dtype=np.int8)
        self.sequence_arr.insert(
            1,
            f"{position}_base",
            np.array(list(map(int, _base_arr)), dtype=np.int16),
            allow_duplicates=True
        )

