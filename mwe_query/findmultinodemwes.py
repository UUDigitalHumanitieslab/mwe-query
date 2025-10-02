from lxml import etree
from sastadev.treebankfunctions import getsentence

treebankfullname = './indexes/mwelexicon_treebank.xml'


def core():
    fulltreebank = etree.parse(treebankfullname)
    treebank = fulltreebank.getroot()
    for tree in treebank:
        topnodes = tree.xpath('.//node[@cat="top"]')
        sentence = getsentence(tree)
        if len(topnodes) == 0:
            print('No topnode for {sentence}')
        elif len(topnodes) > 1:
            print(f'Multiple topnodes in {sentence}')
        else:
            topnode = topnodes[0]
            if len(topnode) > 1:
                print(f'Multinodes for {sentence}')


if __name__ == '__main__':
    core()
