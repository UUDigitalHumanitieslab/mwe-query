import os
from lxml import etree
from sastadev.treebankfunctions import getsentence, showtree
from mwe_query.canonicalform import generatequeries, expandfull

debug = False


def getuttandparse(filename, folder='./testparses'):
    fullname = os.path.join(folder, filename)
    fulltree = etree.parse(fullname)
    tree = fulltree.getroot()
    utterance = getsentence(tree)
    return utterance, tree


def trysomemwes():
    testset = []

    # utterance, uttparse = getuttandparse('_its_sonar_acc_Data_Treebank_MEDIARGUS_COMPACT_NB2005_NB_20050930_01_data_dz_9011.xml')
    # mwe = 'iemand zal 0een *+varken wassen'
    utterance, uttparse = getuttandparse('2058.xml')
    mwe = 'iemand zal 0een L:aanval  OIA:op iemand DO:doen'
    testset.append((mwe, utterance, uttparse))

    for mwe, utterance, uttparse in testset:
        mwequeries = generatequeries(mwe)
        labeledmwequeries = (
            ("MWEQ", mwequeries[0]),
            ("NMQ", mwequeries[1]),
            ("MLQ", mwequeries[2]),
        )
        print(f'MEQ:\n{mwequeries[0]}')
        print(f"{utterance}:")
        expandeduttparse = expandfull(uttparse)
        showparses = True
        if showparses:
            showtree(expandeduttparse, "expandeduttparse")
        for label, mwequery in labeledmwequeries:
            results = expandeduttparse.xpath(mwequery)
            if debug:
                print("Found hits:")
                for result in results:
                    etree.dump(result)
            print(f"{label}: {len(results)}")


if __name__ == "__main__":
    trysomemwes()
