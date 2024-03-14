#!/usr/bin/env python3
"""
Run the commands and write their output
"""

from alpino_query import parse_sentence  # type: ignore
import sys
from os import listdir, path
import glob
import lxml.etree as ET

testdir = path.dirname(__file__)
datadir = path.join(testdir, "data")

# import this implementation
sys.path.insert(0, path.join(testdir, ".."))
from mwe_query import Mwe
from mwe_query.canonicalform import (
    preprocess_MWE,
    transformtree,
    generatemwestructures,
    generatequeries,
    applyqueries,
)

from mwe_query.mwestats import (
    displayfullstats,
    getstats,
    gettreebank,
)


def datapath(dirname, filename):
    return path.join(datadir, dirname, filename)


def read(dirname, filename):
    with open(datapath(dirname, filename)) as f:
        return f.read()


def write(dirname, filename, content):
    with open(datapath(dirname, filename), "w") as f:
        f.write(content)


def update_generate(basename):
    lines = read("generate", basename + ".txt").splitlines()
    can_form = lines[0].strip()
    sentence = lines[1].strip()

    alpino_xml_filename = basename + ".xml"
    if not path.exists(datapath("generate", alpino_xml_filename)):
        print("parsing")
        alpino_xml = parse_sentence(can_form)
        write("generate", alpino_xml_filename, alpino_xml)
    else:
        alpino_xml = read("generate", alpino_xml_filename)

    mwe = Mwe(sentence)
    mwe.set_tree(alpino_xml)

    # This generates a list of MweQuery-objects
    queries = mwe.generate_queries()

    for query in queries:
        write("generate", f"{basename}-{query.rank}.xpath", query.xpath)


def gettopnode(stree):
    for child in stree:
        if child.tag == "node":
            return child
    return None


def update_full_mwe_stats(treebank_name: str, mwe: str):
    dotbfolder = datapath("mwetreebanks", treebank_name)
    rawtreebankfilenames = listdir(dotbfolder)
    selcond = lambda _: True
    treebankfilenames = [
        path.join(dotbfolder, fn)
        for fn in rawtreebankfilenames
        if fn[-4:] == ".xml" and selcond(fn)
    ]
    treebank = gettreebank(treebankfilenames)

    mwestructures = generatemwestructures(mwe)
    for i, mweparse in enumerate(mwestructures):
        mwequery, nearmissquery, supersetquery, relatedwordquery = generatequeries(mwe)
        queryresults = applyqueries(
            treebank, mwe, mwequery, nearmissquery, supersetquery, verbose=False
        )

        fullmwestats = getstats(mwe, queryresults, treebank)

        filename = f"full_mwe_stats_{treebank_name}_{i}.txt"
        outputfilename = datapath(path.join("mwetreebanks", "expected"), filename)

        with open(outputfilename, "w", encoding="utf8") as outfile:

            displayfullstats(
                fullmwestats.mwestats, outfile, header="*****MWE statistics*****"
            )
            displayfullstats(
                fullmwestats.nearmissstats,
                outfile,
                header="*****Near-miss statistics*****",
            )
            displayfullstats(
                fullmwestats.diffstats,
                outfile,
                header="*****Near-miss - MWE statistics*****",
            )


def update_transform():
    mwes = read("transform", "mwes.txt").splitlines()

    i = 0
    for mwe in mwes:
        annotatedlist = preprocess_MWE(mwe)
        annotations = [el[1] for el in annotatedlist]
        fullmweparse = ET.fromstring(read("transform", "tree.xml"))
        mweparse = gettopnode(fullmweparse)
        newtrees = transformtree(mweparse, annotations)

        j = 0
        for newtree in newtrees:
            ET.indent(newtree)
            write("transform", f"{i}-{j}.xml", ET.tostring(newtree, encoding="unicode"))
            j += 1

        i += 1


input_files = glob.glob(path.join(datadir, "generate", "*.txt"))
for input in input_files:
    head, ext = path.splitext(path.basename(input))
    update_generate(head)

update_full_mwe_stats("dansontspringena", "iemand zal de dans ontspringen")
update_full_mwe_stats("hartbreken", "iemand zal iemands hart breken")
update_transform()
