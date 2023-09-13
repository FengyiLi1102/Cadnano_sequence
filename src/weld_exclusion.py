import argparse
import ast
import glob
import json
import os
from collections import defaultdict
from typing import Dict, List

import pandas as pd

import logging

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace):
    """
    Provided inactive well positions, the newly added overhangs (and modified staples) should be filtered out.
    :param args:
    :return:
    """
    # load configuration file
    with open(args.config_path, "r") as f:
        config = json.load(f)
        color_setting = config["colors"]

    # load order csv
    order_csv = pd.read_csv(args.well_path, delimiter=",", usecols=["Bases", "Sequence", "Well Position"])
    order_csv["Sequence"] = ["".join(s.split(" ")) for s in order_csv["Sequence"]]
    # order_csv.to_csv("new_coa.csv", index=False)

    # load design csv files and find overhangs
    sequence_position = defaultdict(list)  # for searching

    for csv_path in glob.glob(os.path.join(args.designs_path, "*.csv")):
        csv_file_name = csv_path.split("/")[-1]
        csv_name = csv_file_name.split(".")[0]
        design_csv = pd.read_csv(csv_path, delimiter=",", usecols=["Sequence", "Length", "Color"])

        # non-modified: added overhangs and modified staples
        # find_non_modified_condition = ~[
        #     design_csv["Sequence"].str.contains("?") & design_csv["Color"] != color_setting["modified_staples"]]
        common_condition = design_csv["Color"] != color_setting["side_overhang"]

        if args.modified:
            # staples excluding side overhangs and including other overhangs or modified ones
            find_required_staples_condition = common_condition & ((design_csv["Sequence"].str.contains("\?")) | (
                    design_csv["Color"] == color_setting["modified_staples"]))
        else:
            # staples excluding side overhangs and including just side overhangs
            find_required_staples_condition = common_condition & design_csv["Sequence"].str.contains("\?")

        sequence_filtered = design_csv[find_required_staples_condition]["Sequence"].tolist()
        sequence_filtered_assigned_part = ["".join(s.split("?")) for s in sequence_filtered]

        for sequence in sequence_filtered_assigned_part:
            start = csv_name.find('(')
            end = csv_name.find(')', start)
            pos = csv_name[start:end + 1]
            sequence_position[sequence].append(pos)

    # search the well positions that should be replaced
    location = []

    for idx, row in order_csv.iterrows():
        # overhang extends from the existing inactive staple without modifying
        the_origami = has_replaced_well(row["Sequence"], sequence_position)

        if the_origami:
            location.append(", ".join(the_origami))
        else:
            # TODO: another feature to confirm whether the target staple actually is one staple that was modified
            location.append("")
            pass

    # create a new order csv to record wells that should be excluded
    order_csv["Exclusion"] = location
    order_csv.to_csv("../results/test_well.csv", index=False)

    pass


def has_replaced_well(target_sequence: str, sequence_pool: Dict[str, List[str]]):
    # TODO: At the moment, we do not replace the staples modified at the top and bottom part of the origami
    """
    FIXME:
        original staples will not have the exactly same sequence as the overhangs so have to find a method to
        compare target sequence and overhang sequence. Bases cannot be chosen too few otherwise the matching
        will be prone to error produced by coincidence.
        For overhangs, this comparison is only required to be conducted on several bases at the beginning.`
    """
    if target_sequence in sequence_pool:
        return sequence_pool[target_sequence]
    else:
        logger.warning(f"Staple with sequence {target_sequence} cannot match with the raw inactive staples.")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--well_path",
                        type=str,
                        default="../sequence_files/coa_copy.csv")
    parser.add_argument("--designs_path",
                        type=str,
                        default="../sequence_files/design_v2_1")
    parser.add_argument("--config_path",
                        type=str,
                        default="../config_v2.JSON")
    parser.add_argument("--modified",
                        action="store_true")

    args = parser.parse_args()

    main(args)
