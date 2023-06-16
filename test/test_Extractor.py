import unittest
from src.ExtendedDNAOrigami import ExtendedDNAOrigami
from src.Extractor import Extractor
from test.utils import args_generator


class MyTestCase(unittest.TestCase):

    def test_extract_function(self):
        test_ext_ori = ExtendedDNAOrigami.load_design(args_generator("../config.JSON"))
        results = Extractor.extract(test_ext_ori)

        self.assertEqual(results[(1, 0)], dict(), "Error: Empty for raw tile")

        self.assertEqual(len(results[(0, 0)]["r"]), 6, "Error: Should be 11 stales added at RHS")
        self.assertEqual(len(results[(0, 0)]["b"]), 9, "Error: Bottom added staples are 9")
        self.assertEqual(len(results[0, 0]["normal"]), 5, "ERROR: Normal staples should be 5")

        self.assertEqual(results[(0, 0)]["r"][0].get_helix_index(), (0, 1), "ERROR: Incorrect sorting results")
        self.assertEqual(results[(0, 0)]["b"][0].get_base_index(), (23, 8), "ERROR: Incorrect sorting results")

    def test_extract_function_on_2_1_structure(self):
        test_ext_ori = ExtendedDNAOrigami.load_design(args_generator("../config_2_1.JSON"))

        results = Extractor.extract(test_ext_ori)

        self.assertEqual(len(results[(0, -1)]["t"]), 9, "Error: Bottom added staples are 9")

        self.assertEqual(results[(0, -1)]["t"][0].get_base_index(), (9, 24), "ERROR: Incorrect sorting results")
        self.assertEqual(results[(0, -1)]["t"][-1].get_base_index(), (271, 279), "ERROR: Incorrect sorting results")


if __name__ == '__main__':
    unittest.main()
