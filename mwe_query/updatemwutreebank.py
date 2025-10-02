"""
ad-hoc script to modify the trees in the mwutreebank so that the non-head words are expanded
"""
from lxml import etree
from canonicalform import expandnonheadwords


def updatemwus():
    mwutreebankfullname = './indexes/mwutreebank.xml'
    newmwutreebankfullname = './indexes/new_mwutreebank.xml'
    fullmwutreebank = etree.parse(mwutreebankfullname)
    mwutreebank = fullmwutreebank.getroot()
    newmwutreebank = etree.Element('treebank')
    for mwutree in mwutreebank:
        newmwutree = expandnonheadwords(mwutree)
        newmwutreebank.append(newmwutree)

    newfullmwutreebank = etree.ElementTree(newmwutreebank)
    newfullmwutreebank.write(
        newmwutreebankfullname, encoding="UTF8", xml_declaration=False, pretty_print=True
    )


if __name__ == '__main__':
    updatemwus()
