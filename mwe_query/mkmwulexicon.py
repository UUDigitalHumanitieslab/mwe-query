from mwutreebank import mwutreebankdict, mwutreebankfullname
from lxml import etree
from tbfstandin import getyieldstr, writetb
import copy
from sastadev.alpinoparsing import parse

mwetreebankfullname = './indexes/mwelexicon_treebank.xml'


def mkmwulexicon():
    fullmwetreebank = etree.parse(mwetreebankfullname)
    mwetreebank = fullmwetreebank.getroot()
    counter = 0
    for tree in mwetreebank:
        counter += 1
        if counter % 100 == 0:
            print(f'{counter} mwes done')
        mwunodes = tree.xpath('.//node[@cat="mwu"]')
        for mwunode in mwunodes:
            mwustr = getyieldstr(mwunode)
            if mwustr in mwutreebankdict:
                newtree = copy.deepcopy(mwutreebankdict[mwustr])
            else:
                print(f'parsing {mwustr}...')
                newtree = parse(mwustr)
                if newtree is None:
                    print(f'no parse found for {mwustr}')
                mwutreebankdict[mwustr] = copy.deepcopy(newtree)

    writetb(mwutreebankdict, mwutreebankfullname)


if __name__ == '__main__':
    mkmwulexicon()
