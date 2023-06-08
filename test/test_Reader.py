import argparse
import unittest

from src.Reader import Reader
from src.constants import *


class MyTestCase(unittest.TestCase):
    # Create parser arguments
    parser = argparse.ArgumentParser("Test reader")
    parser.add_argument("--input_path", "-ip",
                        type=str,
                        default="../sequence_files/staple_tile_TL_v2.csv")
    args = parser.parse_args()

    # Initialise the reader
    reader_test = Reader(args)

    def test_csv_loading(self):
        self.assertEqual(len(self.reader_test.sequence_arr.columns), 7, "Number of columns is not correct.")

        # Test sequences assigned
        args = self.parser.parse_args(["--input_path", "../sequence_files/sequence_not_assigned.csv"])
        with self.assertRaises(Exception):
            no_seq_csv = Reader(args)

        # Test wrong color used
        args = self.parser.parse_args(["--input_path", "../sequence_files/sequence_wrong_color.csv"])
        with self.assertRaises(Exception):
            wrong_color_csv = Reader(args)

    def test_column_split(self):
        self.assertEqual(self.reader_test.sequence_arr.iloc[0, 1], 255)
        self.assertEqual(self.reader_test.sequence_arr.iloc[0, 3], 248)


if __name__ == '__main__':
    unittest.main()
