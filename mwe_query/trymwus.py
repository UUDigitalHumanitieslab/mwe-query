from lxml import etree
import os
from .mwus import get_mwuprops
from sastadev.treebankfunctions import getattval as gav

mwuxpath = './/node[@cat="top"]/node[@cat="mwu"]'


def trymwus():
    mwetreebankfilename = "mwelexicon_treebank.xml"
    mwetreebankpath = "indexes"
    mwetreebankfullname = os.path.join(mwetreebankpath, mwetreebankfilename)

    fulltreebank = etree.parse(mwetreebankfullname)
    treebank = fulltreebank.getroot()
    for stree in treebank:
        mwutrees = stree.xpath(mwuxpath)
        if mwutrees != []:
            mwutree = mwutrees[0]
            mwuroot = gav(mwutree, "mwu_root")
            headnode, pos, headposition = get_mwuprops(mwutree)
            print(mwuroot, pos, headposition)


if __name__ == "__main__":
    trymwus()
