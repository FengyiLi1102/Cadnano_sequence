from __future__ import annotations

import csv
import glob
import os
from copy import copy
from typing import Tuple, Dict, List

from src.Assigner import Assigner
from src.DNAOrigami import DNAOrigami
from src.ExtendedDNAOrigami import ExtendedDNAOrigami
from src.Staple import Staple

import logging

from src.utils import config_logging

config_logging()
logger = logging.getLogger(__name__)


class Generator:
    __config_name: str
    __origami_loc_staples_dict: Dict[Tuple, Dict[str, List[Staple]]] = dict()
    __origami_position_dict: Dict[Tuple, DNAOrigami] = dict()

    __notation_equal = "=" * 64
    __notation_larger = ">" * 3

    __location_filler = {
        "t": "Top",
        "b": "Bottom",
        "r": "Right",
        "l": "Left",
        "modified": "modified"
    }

    @classmethod
    def load_data(cls, assigner: Assigner, extended_dna_origami: ExtendedDNAOrigami) -> Generator:
        generator = cls()

        # load origami positions
        generator.__origami_position_dict = extended_dna_origami.get_origami_position()

        # load assigned overhangs and added normal staples
        generator.__origami_loc_staples_dict = assigner.get_input_origami_staples()

        return generator

    def export_only_bases_added(self, args):
        result_name = self.__generate_results_name(args.save_path)
        tags = ["Start", "End", "Sequence", "Length", "Color"]

        logger.info(f"{self.__notation_equal} Export bases {self.__notation_equal} \n"
                    f"CSV files saved to {args.save_path} \n"
                    f"{self.__notation_equal}=============={self.__notation_equal}")

        save_folder_path = self.__check_save_dir(args.save_path, result_name)

        for origami_pos, tbrlnm_staples_dict in self.__origami_loc_staples_dict.items():
            logger.info(f"Origami:  {self.__origami_position_dict[origami_pos].origami_name} \n"
                        f"Position: {origami_pos}")
            logger.info(f"{self.__notation_larger} Create new csv file")

            with open(os.path.join(save_folder_path, f'{args.save_name}_{origami_pos}.csv'), 'w',
                      newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=tags)
                writer.writeheader()

                for staples_loc, staples_list in tbrlnm_staples_dict.items():
                    if staples_loc == "modified" and not args.modified:
                        continue

                    logger.info(f"{self.__notation_larger} Write in {self.__location_filler[staples_loc]} data")
                    for data in zip(*Staple.read_staple_data(staples_list).values()):
                        writer.writerow(dict(zip(tags, data)))

                    logger.info(f"{self.__notation_larger} Finish writing and save csv file")

    def export_bases_in_original_csv(self, args):
        if not args.save_name:
            result_name = self.__generate_results_name(args.save_path)
        else:
            result_name = args.save_name

        logger.info(f"{self.__notation_equal} Export bases {self.__notation_equal} \n"
                    f"CSV files saved to {args.save_path} \n"
                    f"{self.__notation_equal}=============={self.__notation_equal}")

        save_folder_path = self.__check_save_dir(args.save_path, result_name)

        for origami_pos, dna_origami in self.__origami_position_dict.items():
            # position (a, b) : DNAOrigami
            origami_name = dna_origami.origami_name

            logger.info(f"Origami:  {origami_name} \n"
                        f"Position: {origami_pos}")
            logger.info(f"{self.__notation_larger} Create a copy of {origami_name} csv file")

            dna_origami.csv_df_copy.to_csv(f"{save_folder_path}/all_staples_{origami_pos}_{result_name}.csv",
                                           index=False)

        logger.info(f">>> Finish writing and save all {len(self.__origami_position_dict)} csv files to "
                    f"{save_folder_path}")

    @staticmethod
    def __check_save_dir(save_path: str, result_name: str) -> str:
        save_folder_path = os.path.join(save_path, result_name)
        if not os.path.exists(save_folder_path):
            os.mkdir(save_folder_path)

        return save_folder_path

    @staticmethod
    def __generate_results_name(save_path: str) -> str:
        folder_path = os.path.join(save_path, "res_*")
        all_files_and_folders = glob.glob(folder_path)

        # Filter out just the directories
        directories = [name for name in all_files_and_folders if os.path.isdir(name)]
        if not directories:
            return "res_0"

        directories.sort(key=lambda x: int(x.split('_')[1]))
        largest_integer = int(directories[-1].split('_')[1])

        return f"res_{str(largest_integer + 1)}"


if __name__ == "__main__":
    pass
