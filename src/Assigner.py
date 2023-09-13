from collections import defaultdict
from typing import Tuple, Dict, List
import random

from src.DNAOrigami import DNAOrigami
from src.Staple import Staple
from src.constants import ASSIGNED, UNASSIGNED, NOT_EXIST, COMPLEMENTARY_MAP, HELIX_COMPLEMENTARY_BASE_LEFT_DICT, \
    HELIX_COMPLEMENTARY_BASE_RIGHT_DICT

import logging

from src.utils import config_logging

config_logging()
logger = logging.getLogger(__name__)


class Assigner:
    """
    Assign bases to overhangs for connecting origami components.
    """
    __finished_origami_staples: Dict[Tuple, Dict[str, List[str]]] = dict()  # results of assigned staples
    __input_origami_staples: Dict[Tuple, Dict[str, List[Staple]]] = dict()  # input

    # store assigned bases for further complementary base-pairing
    # Origami chip: staple positions: ((location info), sequence)
    # sequence always from smaller base index to larger one (8 -> 16)
    # NOTE: not complete sequence but only assigned one
    __origami_bases_assigned: Dict[Tuple, Dict[str, Dict[Tuple, str]]] = dict()

    # tuple position and its corresponding DNA origami object
    __origami_position: Dict[Tuple[int, int], DNAOrigami] = dict()

    # temporary dict to store location: overhang position: sequence
    __loc_overhang_sequence_dict: Dict[str, Dict[Tuple, str]] = None

    # temporary dict to store location: list of finished assigning sequence
    __processed_loc_staples: Dict[str, List[str]] = None

    # convert between paired and unassigned overhang locations
    __unassigned_paired_loc_converter = {
        "b": "t",
        "t": "b"
    }

    # Processed origami chip; for assigning bottom and top overhangs
    # Left and right overhangs currently only attach with scaffolds so not require this
    __job_record: Dict[Tuple, int] = dict()

    def assign_bases(self, all_origami_loc_staples_dict: Dict[Tuple, Dict[str, List[Staple]]],
                     origami_position: Dict[Tuple[int, int], DNAOrigami]) -> None:
        # Initialisation
        self.__input_origami_staples = all_origami_loc_staples_dict
        self.__job_record = dict.fromkeys(list(self.__input_origami_staples.keys()), UNASSIGNED)
        self.__origami_position = origami_position

        # Based on the staple sequence, position and p8064 scaffolds to assign bases
        # Connection between DNA origami will be achieved by complementary base-pairing
        for origami_pos, six_type_staples_dict in self.__input_origami_staples.items():
            # origami chip : top, right, bottom, and left processed staples / overhangs, modified staples
            self.__processed_loc_staples = defaultdict(list)

            # location of staples: list of finished-assigning sequences
            self.__loc_overhang_sequence_dict = defaultdict(dict)

            for staple_type, staples_list in six_type_staples_dict.items():
                # staple type : list of staples
                # Top and bottom overhangs do not depend on scaffold bases
                if staple_type in ["t", "b"]:
                    self.__assign_top_bottom(staples_list, origami_pos)
                elif staple_type in ["l", "r"]:
                    # left and right overhangs depend on scaffold bases
                    self.__assign_left_right(staples_list, list(six_type_staples_dict.keys()), origami_pos)
                else:
                    # normal staples do not need assignment of bases
                    # modified staples are actually inactive staples between scaffolds
                    self.__processed_loc_staples[staple_type] = Staple.extract_staples_sequences(staples_list)

            if not list(self.__processed_loc_staples.keys()):
                # no assignment at all
                logger.info("Single origami chip is passed, and no base assignment is done for it.")

            self.__finished_origami_staples[origami_pos] = self.__processed_loc_staples
            self.__origami_bases_assigned[origami_pos] = self.__loc_overhang_sequence_dict.copy()
            self.__job_record[origami_pos] = ASSIGNED

        # check correctness
        self.__correctness_check()

    def __assign_top_bottom(self,
                            unassigned_overhangs_list: List[Staple],
                            origami_pos: Tuple):
        """

        :param unassigned_overhangs_list:
        :param origami_pos:
        :return:
        """
        staples_loc = unassigned_overhangs_list[0].get_position()  # these staples' location
        paired_origami_pos = (origami_pos[0], origami_pos[-1] + 1) if staples_loc == "t" \
            else (origami_pos[0], origami_pos[-1] - 1)  # deduce paired staples' location
        top_bottom_state = self.__find_complementary_tb_origami(origami_pos, staples_loc)  # check neighbour origami

        if top_bottom_state == ASSIGNED:
            # assigned: simply assign by complementary base-pairing
            self.__simple_base_pairing(unassigned_overhangs_list, self.__processed_loc_staples, paired_origami_pos,
                                       origami_pos)
        elif top_bottom_state == UNASSIGNED:
            # unassigned: randomly generate bases for the overhang
            self.__assign_randomly(unassigned_overhangs_list, self.__processed_loc_staples, origami_pos)
        else:
            # not exit
            pass

    def __find_complementary_tb_origami(self, orig_pos: Tuple, staple_loc: str) -> int:
        if staple_loc == "t":
            potential_paired_origami = (orig_pos[0], orig_pos[-1] + 1)
        else:
            potential_paired_origami = (orig_pos[0], orig_pos[-1] - 1)

        state = ASSIGNED  # default: paired origami has been assigned

        if potential_paired_origami in list(self.__input_origami_staples.keys()):
            # require base pairing
            if self.__job_record[potential_paired_origami] == UNASSIGNED:
                # paired origami has not been assigned bases
                state = UNASSIGNED  # this origami required to be assigned manually
        else:
            # not available for base pairing
            state = NOT_EXIST

        return state

    def __simple_base_pairing(self, staples_list: List[Staple],
                              store_dict: Dict[str, List[str]],
                              paired_origami_pos: Tuple[int, int],
                              this_origami_pos: Tuple[int, int]):
        """

        :param staples_list:
        :param store_dict:
        :param paired_origami_pos:
        :param this_origami_pos:
        :return:
        """
        unassigned_staples_loc = staples_list[0].get_position()
        paired_staples_loc = self.__unassigned_paired_loc_converter[unassigned_staples_loc]
        pairing_staples = self.__input_origami_staples[paired_origami_pos][paired_staples_loc]

        # Sanity check
        if len(staples_list) != len(pairing_staples):
            raise Exception("Error: Cannot properly form complementary base-pairing due to different number "
                            "of overhangs on two origami")

        for unassigned_staple, assigned_staple in zip(staples_list, pairing_staples):
            # Find corresponding overhang on the other chip with the same base position
            # This is achieved just by 1 - 1 mapping due to the sorted staple lists
            # TODO: not deal with overhangs to scaffolds directly
            paired_bases = self.__origami_bases_assigned[paired_origami_pos][paired_staples_loc][
                assigned_staple.get_base_index()]
            complementary_bases = Assigner.complementary_converter(paired_bases)

            # For further simple base-pairing
            self.__loc_overhang_sequence_dict[unassigned_staples_loc][
                unassigned_staple.get_base_index()] = complementary_bases

            replace_sequence = unassigned_staple.get_sequence()

            # helix with even index
            even = self.__at_even(paired_staples_loc, unassigned_staple)

            # replace unassigned sequences
            assigned_sequence = self.__replace_unassigned_bases(complementary_bases, replace_sequence, even)

            # replace the corresponding sequence in the copy of the original csv
            csv_replaced = self.__origami_position[this_origami_pos].csv_df_copy
            unassigned_sequence_str = "".join(replace_sequence)
            csv_replaced.loc[csv_replaced["Sequence"] == unassigned_sequence_str, "Sequence"] = assigned_sequence

            unassigned_staple.set_sequence(assigned_sequence)  # update sequence of this overhang

            store_dict[unassigned_staples_loc].append(assigned_sequence)

    @staticmethod
    def __at_even(paired_staples_loc: str, this_staple: Staple):
        if paired_staples_loc == "b":
            # connect with top origami
            # the end out of the scaffold has the least helix index
            even = True if min(this_staple.get_helix_index()) % 2 == 0 else False
        elif paired_staples_loc == "t":
            # with bottom
            even = True if max(this_staple.get_helix_index()) % 2 == 0 else False
        else:
            raise Exception("Error: Unknown pairing staple locations provided")

        return even

    @staticmethod
    def __replace_unassigned_bases(fill_bases: str, replace_sequence: List[str], even: bool) -> str:
        if replace_sequence.count('?') != len(fill_bases):
            raise Exception("Error: Cannot properly form complementary base-pairing due to different number "
                            "of bases on two overhangs")

        # rule in Cadnano: staples on the even indexed (include 0) scaffold have sequence from larger base to smaller
        # one; staples on the old indexed-scaffold have sequence from smaller base to larger one.
        if even:
            fill_bases = fill_bases[::-1]

        start_index = replace_sequence.index("?")
        replace_sequence = "".join(replace_sequence)
        replace_sequence = replace_sequence[:start_index] + fill_bases + replace_sequence[
                                                                         start_index + len(fill_bases):]

        return replace_sequence

    @staticmethod
    def complementary_converter(sequence: str) -> str:
        return "".join(map(lambda c: COMPLEMENTARY_MAP.get(c, c), sequence))

    def __assign_randomly(self,
                          staple_list: List[Staple],
                          store_dict: Dict[str, List[str]],
                          this_origami_pos: Tuple[int, int]):
        """

        :param staple_list:
        :param store_dict:
        :param this_origami_pos:
        :return:
        """
        unassigned_staples_loc = staple_list[0].get_position()
        paired_overhang_loc = self.__unassigned_paired_loc_converter[unassigned_staples_loc]

        for staple in staple_list:
            unassigned_sequence = staple.get_sequence()
            unassigned_sequence = "".join(unassigned_sequence)
            start_index = unassigned_sequence.find("?")
            end_index = unassigned_sequence.rfind("?")

            # replace unassigned bases with randomly generated bases
            length = end_index - start_index + 1
            bases = list(COMPLEMENTARY_MAP.keys())
            fill_bases = "".join(random.choice(bases) for _ in range(length))
            assigned_sequence = unassigned_sequence[:start_index] + fill_bases + unassigned_sequence[end_index + 1:]

            # replace the corresponding sequence in the copy of the original csv
            csv_replaced = self.__origami_position[this_origami_pos].csv_df_copy
            unassigned_sequence_str = "".join(staple.get_sequence())
            csv_replaced.loc[csv_replaced["Sequence"] == unassigned_sequence_str, "Sequence"] = assigned_sequence

            staple.set_sequence(assigned_sequence)
            store_dict[unassigned_staples_loc].append(assigned_sequence)

            # write in dynamic storage
            even = self.__at_even(paired_overhang_loc, staple)
            if even:
                fill_bases = fill_bases[::-1]

            self.__loc_overhang_sequence_dict[unassigned_staples_loc][staple.get_base_index()] = fill_bases

    def __assign_left_right(self,
                            staples_list: List[Staple],
                            has_staples_loc_list: List[str],
                            this_origami_pos: Tuple[int, int]):
        """

        :param staples_list:
        :param has_staples_loc_list:
        :param this_origami_pos:
        :return:
        """
        staple_loc = staples_list[0].get_position()

        # if this origami has top overhangs -> the old design shifts 2 helices down
        if "t" in has_staples_loc_list:
            shift = 2
        else:
            shift = 0

        self.__bind_origami(staples_list, staple_loc, shift, this_origami_pos)

    def __bind_origami(self,
                       staples_list: List[Staple],
                       staple_loc: str,
                       shift: int,
                       this_origami_pos: Tuple[int, int]):
        """

        :param staples_list:
        :param staple_loc:
        :param shift:
        :param this_origami_pos:
        :return:
        """
        if staple_loc == "r":
            converter = HELIX_COMPLEMENTARY_BASE_LEFT_DICT
        else:
            converter = HELIX_COMPLEMENTARY_BASE_RIGHT_DICT

        for staple in staples_list:
            out_scaffold_end_helix_idx = staple.get_helix_index()[
                staple.get_base_index().index(max(staple.get_base_index()))]

            even = True if out_scaffold_end_helix_idx % 2 == 0 else False

            # shift for different designs with empty helices above the origami
            complementary_bases = converter[out_scaffold_end_helix_idx - shift]

            self.__loc_overhang_sequence_dict[staple_loc][staple.get_helix_index()] = complementary_bases[::-1]

            # FIXME: assigned bases store from left to right but scaffold complementary bases from right to left
            # now we leave it
            assigned_sequence = self.__replace_unassigned_bases(complementary_bases[::-1], staple.get_sequence(), even)

            # replace the corresponding sequence in the copy of the original csv
            csv_replaced = self.__origami_position[this_origami_pos].csv_df_copy
            unassigned_sequence_str = "".join(staple.get_sequence())
            csv_replaced.loc[csv_replaced["Sequence"] == unassigned_sequence_str, "Sequence"] = assigned_sequence

            staple.set_sequence(assigned_sequence)

            self.__processed_loc_staples[staple_loc].append(assigned_sequence)

    def __correctness_check(self):
        # for each origami chip -> top, bottom, left, right,
        for origami_pos, tbrlnm_staples_dict in self.__input_origami_staples.items():
            shift = 0 if "t" not in list(tbrlnm_staples_dict.keys()) else 2

            for staples_loc, staples_list in tbrlnm_staples_dict.items():
                if staples_loc in ["r", "l"]:
                    # simply compare with the bases from scaffolds
                    for staple in staples_list:
                        if staples_loc == "r":
                            converter = HELIX_COMPLEMENTARY_BASE_LEFT_DICT
                        else:
                            converter = HELIX_COMPLEMENTARY_BASE_RIGHT_DICT

                        out_scaffold_end_helix_idx = staple.get_helix_index()[
                            staple.get_base_index().index(max(staple.get_base_index()))]
                        assigned_bases = self.__origami_bases_assigned[origami_pos][staples_loc][
                            staple.get_helix_index()]
                        complementary_scaffold_bases = converter[out_scaffold_end_helix_idx - shift][::-1]

                        if assigned_bases != complementary_scaffold_bases:
                            raise Exception("Error: Not satisfy complementary base-pair role for \n"
                                            f"{staple} \n"
                                            f"Assigned bases: {assigned_bases} \n"
                                            f"Scaffold helix: {out_scaffold_end_helix_idx - shift} \n"
                                            f"Scaffold bases: {self.complementary_converter(complementary_scaffold_bases)}")

                elif staples_loc in ["t", "b"]:
                    paired_staples_loc = self.__unassigned_paired_loc_converter[staples_loc]
                    paired_origami_pos = (origami_pos[0], origami_pos[-1] + 1) if staples_loc == "t" \
                        else (origami_pos[0], origami_pos[-1] - 1)
                    origami_loc_sequences_list = list(self.__origami_bases_assigned[origami_pos][staples_loc].values())
                    paired_list = list(self.__origami_bases_assigned[paired_origami_pos][paired_staples_loc].values())

                    counter = 0

                    for staple, paired_one in zip(staples_list,
                                                  self.__input_origami_staples[paired_origami_pos][paired_staples_loc]):
                        assigned_bases = origami_loc_sequences_list[counter]
                        paired_bases = self.complementary_converter(paired_list[counter])

                        if assigned_bases != paired_bases:
                            raise Exception(
                                f"Error: Not satisfy complementary base-pair role for \n"
                                f"{staple} \n"
                                f"Assigned bases: {assigned_bases} \n"
                                f"{paired_one} \n"
                                f"Paired bases:   {paired_bases}")

                        counter += 1
                else:
                    # normal or modified staples
                    pass

    def get_finished_origami_staples(self):
        return self.__finished_origami_staples

    def get_origami_bases_assigned(self):
        return self.__origami_bases_assigned

    def get_unassigned_paired_loc_converter(self) -> Dict[str, str]:
        return self.__unassigned_paired_loc_converter

    def get_input_origami_staples(self) -> Dict[Tuple, Dict[str, List[Staple]]]:
        return self.__input_origami_staples
