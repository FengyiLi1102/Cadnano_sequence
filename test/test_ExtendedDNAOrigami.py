import argparse
import unittest

from src.ExtendedDNAOrigami import ExtendedDNAOrigami
from test.utils import args_generator


class MyTestCase(unittest.TestCase):
    args = args_generator("../config_2_1.JSON")

    def test_creation(self):
        test_ext_dna_ori = ExtendedDNAOrigami.load_design(self.args)
        self.assertEqual(test_ext_dna_ori.get_size(), (2, 1))
        self.assertEqual(test_ext_dna_ori.get_color_setting()["data_bit"], "#00ff10")
        self.assertEqual(test_ext_dna_ori.get_origami_position()[(0, -1)].origami_name, "staple_til_v2_BL")
        self.assertEqual(test_ext_dna_ori.get_origami_position()[(0, 0)].position, (0, 0))


if __name__ == '__main__':
    unittest.main()
