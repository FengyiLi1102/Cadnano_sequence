import argparse
import numpy as np
import pandas as pd
from src.constants import GREEN, CYAN, PURPLE, BLACK


class Reader:
    # Sequence input csv file
    sequence_arr: pd.DataFrame = None

    def __init__(self, args: argparse.Namespace):
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
            print(self.sequence_arr["Color"].unique())
            raise Exception("Error: Color standards are not followed")



