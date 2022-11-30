#!/usr/bin/env python3
"""
Unit test for generating a query
"""
import difflib
import unittest
import glob
from os import path

from mwe_query import Mwe


class TestConsole(unittest.TestCase):
    datadir = path.join(path.dirname(__file__), "data", "generate")

    def test(self):
        input_files = glob.glob(path.join(self.datadir, '*.txt'))
        for input in input_files:
            head, ext = path.splitext(path.basename(input))
            self.assert_sentence(head)

    def assert_sentence(self, basename):
        lines = self.read(basename + ".txt").splitlines()
        sentence = lines[1].strip()

        alpino_xml = self.read(basename + ".xml")

        mwe = Mwe(sentence)
        mwe.set_tree(alpino_xml)

        # This generates a list of MweQuery-objects
        queries = mwe.generate_queries()

        for query in queries:
            self.compare_lines(f"{basename}-{query.rank}.xpath", query.xpath)

    def read(self, filename):
        with open(path.join(self.datadir, filename)) as f:
            return f.read()

    def compare_lines(self, filename_expected, actual):
        expected = self.read(filename_expected).split('\n')

        diff_lines = list(difflib.context_diff(
            expected,
            actual.split('\n'),
            filename_expected + ' (expected)',
            filename_expected + ' (actual)'))

        if len(diff_lines) > 0:
            self.fail('\n'.join(line for line in diff_lines))
