import argparse
import os
import random

from src.Assigner import Assigner

from src.ExtendedDNAOrigami import ExtendedDNAOrigami
from src.Extractor import Extractor
from src.Generator import Generator

import logging

logger = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> None:
    # TODO: (feat) Provide customerised option to assign bases for staples
    if args.non_random:
        # random
        random.seed(42)
    else:
        random.seed(random.randint(1, 1000))

    if not os.path.exists(args.save_path):
        os.mkdir(args.save_path)

    # load configuration file containing design information
    extended_origami = ExtendedDNAOrigami.load_design(args)

    # Assign bases for the design
    assigner = Assigner()
    assigner.assign_bases(Extractor.extract(extended_origami), extended_origami.get_origami_position())

    # Create Generator to produce readable results and also export bases
    generator = Generator.load_data(assigner, extended_origami)

    if args.added:
        generator.export_only_bases_added(args)
    else:
        generator.export_bases_in_original_csv(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run script")
    parser.add_argument("--config",
                        type=str,
                        default="demo_config.JSON")
    parser.add_argument("--save_path",
                        type=str,
                        default=f"results/",
                        help="Use relative path to the project root instead of global one")
    parser.add_argument("--save_name",
                        type=str,
                        default=r"demo")
    parser.add_argument("--non_random",
                        action="store_true",
                        help="Generate real random bases for overhangs or fixed random bases by chosing the same seed")
    parser.add_argument("--modified",
                        action="store_true",
                        help="Include staples not overhangs but modified inactive ones between scaffolds")
    parser.add_argument("--added",
                        action="store_true",
                        help="Export results with staples and overhangs with bases assigned or all staples including"
                             " the original unchanged staples in the origami tile")

    args = parser.parse_args()

    run(args)
