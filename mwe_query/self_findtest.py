from .mwe_annotate import annotate, getmwemetacounts
from .mwemeta import mwemetaheader
from sastadev.alpinoparsing import parse
from sastadev.xlsx import add_worksheet, mkworkbook
from sastadev.readcsv import readcsv
from .canonicalform import removeannotations
from .indexes import mwetreebank, mwelexiconfullname
from typing import List, Tuple
from collections import defaultdict

tab = "\t"


def getmisses(
    ilexicon: List[Tuple[int, Tuple[str, str]]], fullrowlist: List[List[str]]
) -> List[List[str]]:
    results = []
    index = defaultdict(list)
    for row in fullrowlist:
        key = row[1]
        index[key].append(row)

    for i, entry in ilexicon:
        dcmid, mwec = entry
        if dcmid not in index:
            results.append([str(i), dcmid, mwec])
    return results


def selftest():
    stophere = 0  # with 0 it will do all, with a positive value n it will stop after n examples
    ilexicon = readcsv(mwelexiconfullname)
    fullmwemetalist = []
    fulldiscardedmwemetalist = []
    fullduplicatemwemetalist = []

    counter = 0
    # ilexicon = [(1, ('DCM00007' , 'iemand zal *vertrouwen in iets hebben'))]
    # ilexicon = [(2,('DCM01659', 'iets zal hand in hand gaan'))]
    # ilexicon = [(3,('DCM00007', 'iemand zal vertrouwen in iets hebben'))]
    # ilexicon = [(4, ('DCM00005', 'iemand zal < veel> ellende over iemand uitstorten'))]
    # ilexicon = [(5, ('DCM07474', 'iets zal zich voordoen'))]
    # ilexicon = [(6, ('DCM01401', 'iemand zal ernaast zitten'))]
    # ilexicon = [(7, ('DCM02078', 'iemand zal iemand beentje lichten'))]
    # ilexicon = [(8, ('DCM02313', 'iemand zal iemand klem hebben'))]
    # ilexicon = [(9, ('DCM02313', 'het zal met onwillige honden kwaad hazen vangen zijn'))]
    # ilexicon = [(10, ('DCM00390', 'brave Hendrik'))]
    # ilexicon = [(11, ('DCM00008', 	'iemand zal <argumenten> kracht bij zetten'))]
    # ilexicon = [(12, ('DCM12317', 'iemand zal 0een L:mededeling DO:doen'))]
    # ilexicon = [(13, ('DCM00454', 'iemand zal 0dat M:varken M:wassen'))]
    # ilexicon = [(14, ('DCM07315', 'iemand zal L:[van het padje af]  BE:zijn'))]
    # ilexicon = [(15, ('XTR00100', 'c:zware shag'))]
    # ilexicon = [(26, ('DCM12326',	'iemand zal 0de *sporen van iets dragen'))]
    # ilexicon += [(27, ('DCM12253',  '0er zal ^geen spoor van iets te bekennen zijn' ))]
    # ilexicon = [(28, ('DCM12709', '0er zal iets van iets aan zijn'))]

    dcmids = []
    for i, entry in ilexicon:
        counter += 1
        if counter == stophere:
            break
        treeid, rawsentence = entry
        dcmids.append(treeid)
        sentence = removeannotations(rawsentence)
        print(sentence)

        if rawsentence in mwetreebank:
            tree = mwetreebank[rawsentence]
        else:
            tree = parse(sentence)
        if tree is not None:
            mwemetalist, discardedmwemetalist, duplicatemwemetalist = annotate(
                tree, treeid
            )
            fullmwemetalist += mwemetalist
            fulldiscardedmwemetalist += discardedmwemetalist
            fullduplicatemwemetalist += duplicatemwemetalist
        else:
            print(f"No parse for {rawsentence}")

    (statsheader, statsrows) = getmwemetacounts(fullmwemetalist, sentcount=counter)
    fullrowlist = [
        mwemeta.torow() for mwemeta in fullmwemetalist if mwemeta is not None
    ]
    enrichedmwemetaheader = mwemetaheader + ["different"]
    enrichedfullrowlist = [
        fullrow + [f"{str(fullrow[1] != fullrow[5])}"] for fullrow in fullrowlist
    ]
    wb = mkworkbook(
        "MWEmetadata.xlsx",
        [enrichedmwemetaheader],
        enrichedfullrowlist,
        freeze_panes=(1, 0),
    )
    add_worksheet(wb, [statsheader], statsrows, sheetname="Stats")
    fullduplicaterows = [mwemeta.torow() for mwemeta in fullduplicatemwemetalist]
    add_worksheet(wb, [mwemetaheader], fullduplicaterows, sheetname="Duplicates")

    wb.close()

    missedones = getmisses(ilexicon, fullrowlist)
    missedfilename = "missedones.txt"
    with open(missedfilename, "w", encoding="utf8") as missedfile:
        for missedone in missedones:
            print(tab.join(missedone), file=missedfile)


if __name__ == "__main__":
    selftest()
