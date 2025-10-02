from canonicalform import transformmwu
from lxml import etree


def tryme():
    inputfiles = [
        r'D:\Dropbox\various\Resources\nl-parseme-lassy70-enhanced\cdb\2473.xml']
    for inputfile in inputfiles:
        fulltree = etree.parse(inputfile)
        tree = fulltree.getroot()
        newtree = transformmwu(tree)
        etree.dump(newtree)


if __name__ == '__main__':
    tryme()
