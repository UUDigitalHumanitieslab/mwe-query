import os
from lxml import etree
from .tbfstandin import getyieldstr

mwutreebankfullname = './indexes/mwutreebank.xml'
mwutreebankdict = {}

if os.path.exists(mwutreebankfullname):
    fulltreebank = etree.parse(mwutreebankfullname)
    treebank = fulltreebank.getroot()
    for tree in treebank:
        mwustr = getyieldstr(tree)
        mwutreebankdict[mwustr] = tree

junk = 0
