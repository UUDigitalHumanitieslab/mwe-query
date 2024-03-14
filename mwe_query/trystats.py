import os
from .mwestats import gettreebank
from .mkpivothtmls import createstatshtmlpages


def test():
    # mwes,  dotbfolder, treebankname = ['iemand zal 0de *dans ontspringen'], r'../tests/data/mwetreebanks/dansontspringena', 'Lassy-Groot/Kranten'
    # mwes, dotbfolder, treebankname =  ['iemand zal iemands hart breken'], r'../tests/data/mwetreebanks/hartbreken/data','Lassy-Groot/Kranten'
    mwes, dotbfolder, treebankname = (
        ["iemand zal 0een L:poging DO:doen"],
        r"..\tests\data\mwetreebanks\pogingdoen",
        "Lassy-Groot/Kranten",
    )
    rawtreebankfilenames = os.listdir(dotbfolder)

    def selcond():
        return True

    # selcond = lambda x: x == 'WR-P-P-G__part00357_3A_3AWR-P-P-G-0000167597.p.8.s.2.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00788_3A_3AWR-P-P-G-0000361564.p.1.s.4.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00012_3A_3AWR-P-P-G-0000006175.p.6.s.3.xml'
    # selcond = lambda x: x == 'WR-P-P-G__part00160_3A_3AWR-P-P-G-0000081644.p.10.s.4.xml'
    treebankfilenames = [
        os.path.join(dotbfolder, fn)
        for fn in rawtreebankfilenames
        if fn[-4:] == ".xml" and selcond(fn)
    ]
    treebank = gettreebank(treebankfilenames, filenameid=True)
    # _, treebankname = os.path.split(dotbfolder)
    for mwe in mwes:
        createstatshtmlpages(mwe, treebank, treebankname)


if __name__ == "__main__":
    test()
