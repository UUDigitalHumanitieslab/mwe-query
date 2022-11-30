import unittest

import xml.etree.ElementTree as ET
from mwe_query import expand_index_nodes

class TextIndexExpansion(unittest.TestCase):

    def test_no_infinite_loop(self):
        with open('tests/data/expand/001.xml') as f:
            doc = ET.parse(f)
            expand_index_nodes(doc)
