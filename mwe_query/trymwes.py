from sastadev.alpinoparsing import parse
from lcat import expandnonheadwords
from sastadev.treebankfunctions import indextransform
from lxml import etree
from canonicalform import generatequeries, expandfull

debug = False

geenhaankraaien = ('0geen *haan zal naar iets kraaien',
                   ['Daar kraait geen haan naar', 'Hier heeft geen haan naar gekraaid',
                    'geen haan kraaide daarnaar', 'geen haan kraaide ernaar dat hij niet kwam',
                    'geen haan kraaide er naar dat hij niet kwam', 
                    'er is geen haan die daar naar kraait', ]
                   )

def select(mweutts, utt=None):
    if utt is None:
        result = mweutts
    else:
        result = (mweutts[0], [mweutts[1][utt]])
    return result

def getparses(utterances):
    uttparses = []
    for utterance in utterances:
        uttparse = parse(utterance)
        uttparses.append(uttparse)
    return uttparses

def trysomemwes():
    mwe, utterances = select(geenhaankraaien)
    mwequeries = generatequeries(mwe)
    labeledmwequeries = (('MWEQ', mwequeries[0]), ('NMQ', mwequeries[1]), ('MLQ', mwequeries[2]))
    uttparses = getparses(utterances)
    for utterance, uttparse in zip(utterances, uttparses):
        print(f'{utterance}:')
        expandeduttparse = expandfull(uttparse)
        if debug:
            etree.dump(expandeduttparse)
        for label, mwequery in labeledmwequeries:
            results = expandeduttparse.xpath(mwequery)
            if debug:
                print('Found hits:')
                for result in results:
                    etree.dump(result)
            print(f'{label}: {len(results)}')




if __name__ == '__main__':
    trysomemwes()