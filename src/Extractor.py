from collections import defaultdict
from typing import List, Dict, Tuple

import pandas as pd

from src.ExtendedDNAOrigami import ExtendedDNAOrigami
from src.Staple import Staple

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)


class Extractor:
    """
    Extract staples information from each origami component.
    """

    @classmethod
    def extract(cls, extended_origami: ExtendedDNAOrigami) -> Dict[Tuple, Dict[str, List[Staple]]]:
        """
        Extract overhangs and normal staples.
        :param cls: class
        :param extended_origami: Extended DNA origami
        :return: five types of staples (left, right, top, bottom, normal) for each origami
        """
        origami_loc_staples_dict = dict()
        side_color = extended_origami.get_color_setting()["side_overhang"]
        other_color = extended_origami.get_color_setting()["other_overhang"]

        for origami_pos, origami_chip in extended_origami.get_origami_position().items():
            # Group the dataframe by colors, and find overhangs
            csv_df_copy = origami_chip.get_csv_df().copy()
            grouped_df = csv_df_copy.groupby("Color")

            location_staples = defaultdict(list)  # store locations and associated staples for each origami

            for loc, color in enumerate([other_color, side_color]):
                if color in grouped_df.groups.keys():
                    # origami possibly has overhangs
                    color_group = grouped_df.get_group(color)  # staples in this color
                    color_group = Extractor.sort_staples_for_output(color_group, loc)  # Sort the staples for output
                    cls.filter_staple_by_location(color_group, location_staples, extended_origami)

            origami_loc_staples_dict[origami_chip.position] = location_staples

        return origami_loc_staples_dict

    @staticmethod
    def sort_staples_for_output(groupby_obj: pd.DataFrame, side: int) -> pd.DataFrame:
        """
        Sort grouped-by-color dataframe from left to right based on base index and from top to bottom based on helix
        index.
        :param groupby_obj: grouped dataframe object with one color
        :param side: condition (0 for top or bottom staples and 1 for sided staples)
        :return: sorted dataframe
        """
        groupby_obj_copy = groupby_obj.copy()

        # find the end out of the scaffold and use it to sort
        # TODO: two ends both out of the scaffold
        if side:
            # right or left
            groupby_obj_copy["compare"] = groupby_obj_copy.apply(
                lambda row: row["Start"] if row["Start_base"] > row["End_base"] else row["End"], axis=1)
        else:
            # top or bottom
            groupby_obj_copy["compare"] = groupby_obj_copy.apply(
                lambda row: row["Start_base"] if row["Start"] > row["End"] else row["End_base"], axis=1)

        groupby_obj_copy = groupby_obj_copy.sort_values(by="compare", ascending=True)
        del groupby_obj_copy["compare"]

        return groupby_obj_copy

    @staticmethod
    def filter_staple_by_location(group_df: pd.DataFrame, location_staples: Dict[str, List[Staple]],
                                  extended_origami: ExtendedDNAOrigami) -> None:
        """
        Classify staples by their locations determined before.
        :param group_df: grouped staple dataframe by the color
        :param location_staples: dict to store staples of different locations
        :param extended_origami: extended origami object
        :return: None
        """
        for idx, row in group_df.iterrows():
            staple = Staple(row, extended_origami.get_color_setting())

            if staple.is_overhang:
                location_staples[staple.get_position()].append(staple)
            else:
                location_staples["normal"].append(staple)
