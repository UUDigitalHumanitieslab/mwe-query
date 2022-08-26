#!/usr/bin/env python3
"""
Run the commands and write their output
"""

from alpino_query import parse_sentence
import sys
from os import path
import glob

testdir = path.dirname(__file__)
datadir = path.join(testdir, "data")

# import this implementation
sys.path.insert(0, path.join(testdir, ".."))
from mwe_query import Mwe


def datapath(filename):
    return path.join(datadir, filename)


def read(filename):
    with open(datapath(filename)) as f:
        return f.read()


def write(filename, content):
    with open(datapath(filename), "w") as f:
        f.write(content)


def update(basename):
    lines = read(basename + ".txt").splitlines()
    can_form = lines[0].strip()
    sentence = lines[1].strip()

    alpino_xml_filename = basename + ".xml"
    if not path.exists(datapath(alpino_xml_filename)):
        print("parsing")
        alpino_xml = parse_sentence(can_form)
        write(alpino_xml_filename, alpino_xml)
    else:
        alpino_xml = read(alpino_xml_filename)

    mwe = Mwe(sentence)
    mwe.set_tree(alpino_xml)

    # This generates a list of MweQuery-objects
    queries = mwe.generate_queries()

    for query in queries:
        write(f"{basename}-{query.rank}.xpath", query.xpath)


input_files = glob.glob(path.join(datadir, '*.txt'))
for input in input_files:
    head, ext = path.splitext(path.basename(input))
    update(head)
