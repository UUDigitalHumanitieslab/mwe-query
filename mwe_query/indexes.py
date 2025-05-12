from lxml import etree
from dataclasses import dataclass
from sastadev.treebankfunctions import find1, getattval
from canonicalform import preprocess_MWE, transformtree, gettopnode, mwenormalise, tokenize, vblwords, \
    transformalsvz, transformadvprons, expandnonheadwords, transformmwu
from wordtransform import correctlemmas
from lexicons import lemmacorrectionlexicon
# from mwuwordlemmas import mwuwordlemmadict
from sastadev.sastatypes import SynTree
from sastadev import readcsv
from tbfstandin import writetb

# from dcm2pep import dcm_clean
# from alpino_query import parse_sentence
import sastadev.alpinoparsing
from typing import List, Tuple
import os
import json
import pathlib
import datetime

space = " "

ambigconstant = 100000

modtimefilename = f"{__file__}_previousmodtime.json"
mwelexiconpath = "./mwelexicon"
# mwelexiconfilename = 'DUCAME_3.0.txt'
# mwelexiconfilename = 'DUCAME_4.0.txt'
# mwelexiconfilename = "DUCAME_4.01.txt"
# mwelexiconfilename = "DUCAME_4.02.txt"
mwelexiconfilename = "DUCAME_4.03.txt"
mwelexiconfilename = "DUCAME_4.04.txt"
mwelexiconfilename = "DUCAME_4.05.txt"
# mwelexiconfilename = "testlexicon.txt"  # for testing purposes
mwelexiconfullname = os.path.join(mwelexiconpath, mwelexiconfilename)


@dataclass
class Indexes:
    mweid2id: dict
    id2mweid: dict
    lemma2iddict: dict
    lemmasofmwedict: dict
    mwetreesdict: dict


def iscontentpt(pt: str) -> bool:
    return pt in ["n", "ww", "adj", "bw", "spec"]


def getlemmas(rawmwetree, origutt):

    # transform alsvz, pronadvs, etc
    mwetree1 = expandnonheadwords(rawmwetree)
    mwetree2 = transformalsvz(mwetree1)
    mwetree3 = transformadvprons(mwetree2)
    mwetree4 = correctlemmas(mwetree3)
    mwetree = transformmwu(mwetree4)

    # reduce the tree as is currently don in mwe-finder
    # list all remaining lemma's
    reducedmwetree = reducemwestructure(mwetree)
    lemmanodes = reducedmwetree.xpath(".//node[@lemma]")
    lemmapts = []
    for lemmanode in lemmanodes:
        lemmapt = (getattval(lemmanode, "pt"), getattval(lemmanode, "lemma"))
        lemmapts.append(lemmapt)
    contentlemmapts = [lpt for lpt in lemmapts if iscontentpt(lpt[0])]
    if len(contentlemmapts) > 1:
        results = [lpt[1] for lpt in contentlemmapts]
    else:
        results = [lpt[1] for lpt in lemmapts]
    return results


def getmodtime(filename):
    result = pathlib.Path(filename).stat().st_mtime
    return result


def getatt(mwetree, att):
    result = find1(mwetree, f'.//metadata/meta[@name="{att}"]/@value')
    return result


def putlastmodtime(time):
    with open(modtimefilename, "w", encoding="utf8") as outfile:
        json.dump(time, outfile)


def getlastmodtime():
    if os.path.exists(modtimefilename):
        with open(modtimefilename, "r", encoding="utf8") as outfile:
            time = json.load(outfile)
            return time
    else:
        olddate = datetime.datetime(
            1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        olddatefloat = olddate.timestamp()
        return olddatefloat


def dcm_clean(mwestr: str) -> str:
    aws = preprocess_MWE(mwestr)
    words = [aw[0] for aw in aws]
    result = space.join(words)
    return result


def extendindexesforextralemmas(i: int, mweid: str, lemmas: List[str],
                                mweid2id, id2mweid, lemmasofmwedict, lemma2iddict, mwetreesdict):
    """

    Args:
        i: internal identifier of the mwe (int)
        mweid: external mwe identifier (str)
        lemmas: list of lemmas that are new
        mweid2id: dictionary to be updated
        id2mweid: dictionary to be updated
        lemmasofmwedict: dictionary to be updated
        lemma2iddict: dictionary to be updated
        mwetreesdict: dictionary to be updated

    Returns: None

    """
    # extra lemmas for words in mwus
    # this is not needed anymore
    # extralemmas = getextralemmas(lemmas)
    # k = ambigconstant + i
    # extramweid = f"{mweid}X"
    # if extralemmas != []:
    #     mweid2id[extramweid] = k
    #     id2mweid[k] = extramweid
    #     lemmasofmwedict[k] = extralemmas
    #     for lemma in extralemmas:
    #         if lemma in lemma2iddict:
    #             lemma2iddict[lemma].append(k)
    #         else:
    #             lemma2iddict[lemma] = [k]
    #     mwetreesdict[k] = mwetree


def updateindexes(indexes, mwefilename, forced=False):
    mweid2id = indexes.mweid2id
    id2mweid = indexes.id2mweid
    lemma2iddict = indexes.lemma2iddict
    lemmasofmwedict = indexes.lemmasofmwedict
    mwetreesdict = indexes.mwetreesdict

    mwefilenamelastmodtime = getmodtime(mwefilename)
    thisfilepreviouslastmodtime = getlastmodtime()
    thisfilelastmodtime = getmodtime(__file__)
    putlastmodtime(thisfilelastmodtime)
    indexfilenamelastmodtime = getmodtime(indexfullname)
    treebanklastmodtime = getmodtime(mwetreebankfullname)

    updateneeded = False
    forcedlemmaupdate = False
    if mwefilenamelastmodtime > indexfilenamelastmodtime:
        updateneeded = True
        print(f"Index update needed because {mwefilename} changed")
    if forced:
        updateneeded = True
        print("Index update forced")
    if thisfilelastmodtime > thisfilepreviouslastmodtime:
        updateneeded = True
        print(f"Index update needed because {__file__} changed")
    if treebanklastmodtime > indexfilenamelastmodtime:
        updateneeded = True
        print(f"Index update needed because {mwetreebankfullname} changed")

    if updateneeded:
        # now we have to update the indexes

        baseimwes = readcsv.readcsv(mwefilename)
        imwes = expandimwes(baseimwes)
        # if forced:
        #    print('Forced index update')
        # else:
        #     print(f'mwe lexicon in {mwefilename} more recent than indexes in {indexfilename}\nUpdating indexes...')
        print(f"reading {mwefilename}...")
        mwestrings = set()
        for i, mwe in imwes:
            # if i % 100 == 0:
            #    print(i)
            mweid = mwe[0]
            mwestr = mwe[1]
            mwestrings.add(mwestr)
            if mwestr in mwetreebank:
                mwetree = mwetreebank[mwestr]
            else:
                cleanmwe = dcm_clean(mwestr)
                mwetree = sastadev.alpinoparsing.parse(cleanmwe)
                if mwetree is not None:
                    metadata = etree.Element("metadata")
                    meta1 = etree.Element(
                        "meta",
                        attrib={"type": "text",
                                "name": "origutt", "value": mwestr},
                    )
                    meta2 = etree.Element(
                        "meta", attrib={"type": "text", "name": "id", "value": mweid}
                    )
                    metadata.append(meta1)
                    metadata.append(meta2)
                    mwetree.append(metadata)
                    mwetreebank[mwestr] = mwetree
                else:
                    print(f"No parse found for {mwestr}")
            if mwetree is not None:
                mweid = getatt(mwetree, "id")
                if mweid not in mweid2id or forcedlemmaupdate:
                    rawlemmas = getlemmas(mwetree, mwestr)
                    lemmas = [
                        rawlemma for rawlemma in rawlemmas if rawlemma != "zullen"
                    ]
                    mweid2id[mweid] = i
                    id2mweid[i] = mweid
                    lemmasofmwedict[i] = lemmas
                    for lemma in lemmas:
                        if lemma in lemma2iddict:
                            lemma2iddict[lemma].append(i)
                        else:
                            lemma2iddict[lemma] = [i]
                    mwetreesdict[i] = mwetree

                    # extra lemmas for words in mwus
                    # not needed anymore
                    # extralemmas = getextralemmas(lemmas)
                    # k = ambigconstant + i
                    # extramweid = f"{mweid}X"
                    # if extralemmas != []:
                    #     mweid2id[extramweid] = k
                    #     id2mweid[k] = extramweid
                    #     lemmasofmwedict[k] = extralemmas
                    #     for lemma in extralemmas:
                    #         if lemma in lemma2iddict:
                    #             lemma2iddict[lemma].append(k)
                    #         else:
                    #             lemma2iddict[lemma] = [k]
                    #     mwetreesdict[k] = mwetree

        # schrijf de nieuwe mwetreebank naar file  meerdere keren voor  het geval dat het afgebroken wordt@@
        # niet nodig hier
        # if k % 100 == 0:
        #     writetb(mwetreebank)

        # remove trees from the treebank that are not in the mwe lexicon file
        mwetreesdictkeys = list(mwetreesdict.keys())
        for mwekey in mwetreesdictkeys:
            mwetree = mwetreesdict[mwekey]
            mwestr = getatt(mwetree, "origutt")
            if mwestr not in mwestrings:
                print(f"Removing tree for {mwestr}")
                del mwetreesdict[mwekey]

        writetb(mwetreebank, mwetreebankfullname)
    else:
        print("Indexes up to date")

    indexes = Indexes(mweid2id, id2mweid, lemma2iddict,
                      lemmasofmwedict, mwetreesdict)
    return indexes


def expandimwes(imwes: List[Tuple[int, List[str]]]) -> List[Tuple[int, List[str]]]:
    """

    Args:
        imwes: list of Tuples(counter, mwe

    Returns:
        list of Tuples (counter, mwe) by applying expandmwe to each mwe in the input

    """
    baseresults = []
    for _, mwe in imwes:
        baseresults += expandmwe(mwe)
    results = list(enumerate(baseresults))
    return results


def expandmwe(rawmwe: Tuple[str]) -> List[Tuple[str]]:
    """

    Args:
        rawmwe: a list of 2 elements: mweid, mwestr

    Returns: a list of 2 elements: mweid, mwestr, with the input and where an OIA annotation occurs, a variant with
    the OIA argument left out

    """
    results = [rawmwe]
    mweid = rawmwe[0]
    rawmwestr = rawmwe[1]
    mwestr = mwenormalise(rawmwestr)
    can_form = tokenize(mwestr)
    newresultlist = []
    oiaindex = -2
    oiafound = False
    for i, word in enumerate(can_form):
        if oiaindex == -2 and word.lower().startswith('oia:'):
            oiaindex = i
            oiafound = True
        elif oiaindex == i - 1 and word.lower() in vblwords:
            oiaindex = -1
        else:
            newresultlist.append(word)
    if oiafound:
        newmwestr = space.join(newresultlist)
        newmweid = f'{mweid}a'
        newresult = (newmweid, newmwestr)
        results.append(newresult)
    return results


def getextralemmas(lemmas: List[str]) -> List[str]:
    """
    words in mwus often do not get their proper lemma; in some treebanks they have; here we correct this
    :param lemmas:
    :return:
    """
    newlemmas = []
    for lemma in lemmas:
        # if lemma in mwuwordlemmadict:
        if lemma in lemmacorrectionlexicon:
            newlemma = lemmacorrectionlexicon[lemma]
        else:
            newlemma = lemma
        newlemmas.append(newlemma)
    if newlemmas != lemmas:
        result = newlemmas
    else:
        result = []
    return result


def reducemwestructure(mwetree: SynTree) -> SynTree:
    """
    generate  a structure from which we can select the major lemmas
    :param mwetree:
    :param lcatexpansion:
    :return:
    """
    mwe = getatt(mwetree, "origutt")
    annotatedlist = preprocess_MWE(mwe)
    annotations = [el[1] for el in annotatedlist]

    mweparse = gettopnode(mwetree)
    newtrees = transformtree(mweparse, annotations)
    thetree = newtrees[0] if newtrees != [] else None
    return thetree


def getmwetreebank(treebankfilename):
    treebankdict = {}
    fulltreebank = etree.parse(treebankfilename)
    treebank = fulltreebank.getroot()
    for tree in treebank:
        origutt = getatt(tree, "origutt")
        treebankdict[origutt] = tree
    return treebankdict


indexespath = "./indexes"

mwetreebankfilename = "mwelexicon_treebank.xml"
mwetreebankfullname = os.path.join(indexespath, mwetreebankfilename)
mwetreebank = {}
if os.path.exists(mwetreebankfullname):
    mwetreebank = getmwetreebank(mwetreebankfullname)


# initialize the indexes
indexes = Indexes({}, {}, {}, {}, {})

indexespath = "./indexes"
indexfilename = "mweindex.json"
indexfullname = os.path.join(indexespath, indexfilename)
if os.path.exists(indexfullname):  # and older than the source file
    with open(indexfullname, "r", encoding="utf8") as indexfile:
        indexliststr = indexfile.read()
    indexlist = json.loads(indexliststr)
    mwetreesdict = {}
    for mwestr in mwetreebank:
        mwetree = mwetreebank[mwestr]
        dcmid = getatt(mwetree, "id")
        if dcmid in indexlist[0]:
            i = indexlist[0][dcmid]
            mwetreesdict[i] = mwetree
            # dcmidx = f'{dcmid}X'                   # for adding cases with extra lemmas because of MWUs
            # if dcmidx in indexlist[0]:
            #     k = indexlist[0][dcmid] + ambigconstant
            #     mwetreesdict[k] = mwetree
        else:
            print(f"No index entry for {dcmid}: {mwestr} ")
    if len(indexlist) == 4:
        indexes = Indexes(
            indexlist[0], indexlist[1], indexlist[2], indexlist[3], mwetreesdict
        )

# lees nu het mwelexicon in en update de indexes voor mwe's die nog niet voorkomen in de indexes
# print('Updating indexes...')
indexes = updateindexes(indexes, mwelexiconfullname)
indexlist = [
    indexes.mweid2id,
    indexes.id2mweid,
    indexes.lemma2iddict,
    indexes.lemmasofmwedict,
]
indexlistjson = json.dumps(indexlist)
with open(indexfullname, "w", encoding="utf8") as indexfile:
    print(indexlistjson, file=indexfile)


def forcedupdate(infullname):
    indexes = Indexes({}, {}, {}, {}, {})
    forcedupdate = True
    indexes = updateindexes(indexes, infullname, forced=forcedupdate)
    indexlist = [
        indexes.mweid2id,
        indexes.id2mweid,
        indexes.lemma2iddict,
        indexes.lemmasofmwedict,
    ]
    indexlistjson = json.dumps(indexlist)
    with open(indexfullname, "w", encoding="utf8") as indexfile:
        print(indexlistjson, file=indexfile)


if __name__ == "__main__":
    # infullname = 'ducame v300.txt'
    # infullname = "./mwelexicon/ducame_4.01.txt"
    infullname = mwelexiconfullname
    indexes = Indexes({}, {}, {}, {}, {})
    forcedupdate(infullname)

    junk = 0
