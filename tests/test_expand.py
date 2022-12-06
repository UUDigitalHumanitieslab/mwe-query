import unittest
import os

import xml.etree.ElementTree as ET
from mwe_query import expand_index_nodes


class TextIndexExpansion(unittest.TestCase):
    def data_path(self, filename):
        return os.path.join(os.path.dirname(__file__), "data", filename)

    def test_no_infinite_loop(self):
        with open(self.data_path('expand/001.xml')) as f:
            doc = ET.parse(f)
            expand_index_nodes(doc)
