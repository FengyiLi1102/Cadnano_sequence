import argparse
import unittest

from src.DNAOrigami import DNAOrigami
from utils import csv_loader


class MyTestCase(unittest.TestCase):
    # Initialise the reader
    reader_test = csv_loader("../sequence_files/staple_tile_TL_v2.csv")

    def test_csv_loading(self):
        self.assertEqual(len(self.reader_test.get_csv_df().columns), 7, "Number of columns is not correct.")

        # Test sequences assigned
        with self.assertRaises(Exception):
            no_seq_csv = csv_loader("../sequence_files/sequence_not_assigned.csv")

    def test_column_split(self):
        self.assertEqual(self.reader_test.get_csv_df().iloc[0, 1], 255)
        self.assertEqual(self.reader_test.get_csv_df().iloc[0, 3], 248)


if __name__ == '__main__':
    unittest.main()
