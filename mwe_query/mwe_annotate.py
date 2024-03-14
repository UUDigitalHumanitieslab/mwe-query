from collections import Counter
from .getalpinomwes import getalpinomwes
from .indexes import indexes, getatt, mwelexiconfilename as mwelexicon
from itertools import combinations
from lxml import etree
from .mwemeta import isidentical, MWEMeta, meq, nmq, mlq
from .mwetypes import getmweclasses, getmwetype
from .canonicalform import (
    expandaltvals,
    expandfull,
    generatemwestructures,
    generatequeries,
    getmajorlemmas,
    mknearmissstructs,
    preprocess_MWE,
)
from .mwestats import getheadcomponent, getmwecomponents
from .mwus import get_mwuprops
from .pronadvs import allpronadvlemmas, pronadv2vz
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval, getsentence, find1, showtree
from typing import cast, Any, List, Optional, Tuple
import itertools
from .alternatives import expandalternatives
import sys

Mwetype = str
XpathExpression = str
altsym = "|"

mwecomponentsxpath = ".//node[@lemma]"


def getmweheadnode(syntree: SynTree) -> Optional[Tuple[SynTree, str]]:
    topnode = find1(syntree, './/node[@cat="top"]')
    if topnode is not None:
        if len(topnode) == 1:
            topchild = topnode[0]
            candhead = find1(topchild, './node[@rel="hd"]')
            if getattval(topchild, "cat") == "mwu":
                headnode, headpos, headposition = get_mwuprops(topchild)
                result = headnode, headpos
            elif getattval(candhead, "lemma") == "zullen":
                vc = find1(topchild, './node[@rel="vc"]')
                if vc is not None:
                    headnode = find1(vc, './node[@rel="hd"]')
                    result = headnode, getattval(headnode, "pt")
                else:
                    result = None
            elif getattval(candhead, "cat") == "mwu":
                headnode, headpos, headposition = get_mwuprops(candhead)
                result = headnode, headpos

            else:
                result = candhead, getattval(candhead, "pt")
        else:
            result = None
    return result


def getmweheadposition(syntree: SynTree) -> int:
    hdtuple = getmweheadnode(syntree)
    if hdtuple is not None:
        hdnode, hdpos = hdtuple
        hdnodeend = getattval(hdnode, "end")
        if hdnodeend != "":
            result = int(hdnodeend)
        else:
            result = -1
    else:
        result = -1
    return result


def getmweheadlemma(stree: SynTree) -> str:
    hdtuple = getmweheadnode(stree)
    if hdtuple is not None:
        hdnode, hdpt = hdtuple
        result = getattval(hdnode, "lemma")
    else:
        result = ""
    return result


def getmweheadpt(syntree: SynTree) -> str:
    hdtuple = getmweheadnode(syntree)
    if hdtuple is not None:
        hdnode, hdpt = hdtuple
        result = hdpt
    else:
        result = ""
    return result


def getheadnode(syntree: SynTree) -> Optional[SynTree]:
    # etree.dump(syntree)
    # xpexpr = './/node[@cat="top"]/node/node[@rel="hd" and @pt]'
    xpexpr = (
        './node[(@rel="hd" or @rel="cmp") and @pt]'  # this applies to MWE structures
    )
    hdnodes = syntree.xpath(xpexpr)
    if len(hdnodes) >= 1:
        result = hdnodes[0]
    else:
        result = None
    return result


def getlemmas(syntree: SynTree) -> List[str]:
    # lemmanodes = syntree.xpath('.//node[@lemma and not(@rel="svp")]')  # we must exclude svps from the lemmas
    lemmanodes = syntree.xpath(
        ".//node[@lemma]"
    )  # no we must keep svps from the lemmas
    lemmas = []
    for lemmanode in lemmanodes:
        lemma = getattval(lemmanode, "lemma")
        lemmas.append(lemma)
    return lemmas


def adaptlemma(lemma: str) -> List[str]:
    if lemma in allpronadvlemmas:
        vzaz = pronadv2vz(lemma)
        if vzaz is None:
            result = []
        else:
            (vz, az) = vzaz
            if az is None:
                result = [vz]
            else:
                result = [vz, az]
    else:
        result = []
    return result


def adaptlemmas(rawlemmas: List[str]) -> List[str]:
    results = []
    for rawlemma in rawlemmas:
        newlemmas = adaptlemma(rawlemma)
        if newlemmas == []:
            results.append(rawlemma)
        else:
            results.extend(newlemmas)
    return results


def is_subset(list1, list2):
    clist1 = Counter(list1)
    clist2 = Counter(list2)
    for el in clist1:
        if el not in clist2 or clist2[el] < clist1[el]:
            return False
    # result = clist1 <= clist2  # only possible in Python 3.10
    return True


def results2metadata(
    queryresult,
    mwestructures,
    sentence,
    sentenceid,
    origutt,
    mweclasses,
    mwetype,
    mwelexiconid,
    querytype,
):
    # get the components
    componentslist = getmwecomponents([queryresult], mwestructures)
    # components = componentslist[0] if componentslist != [] else []
    mwemetas = []
    for components in componentslist:
        # print('New components')
        headcomponent = getheadcomponent(queryresult, components)
        if headcomponent is not None:
            headposition = int(getattval(headcomponent, "end"))
            headpos = getattval(headcomponent, "pt")
        else:
            headposition = -1
            headpos = "UNK"
        positions = [int(getattval(component, "end")) for component in components]
        sortedpositions = sorted(positions)

        # store the results in metadata
        mwemeta = MWEMeta(
            sentence,
            sentenceid,
            origutt,
            mwelexicon,
            querytype,
            mwelexiconid,
            sortedpositions,
            headposition,
            headpos,
            mweclasses,
            mwetype,
        )
        mwemetas.append(mwemeta)
    if len(mwemetas) >= 1:
        result = mwemetas[0]
    # if len(mwemetas) > 1:  # this always involves duplicates
    #    print(f'mwe_annotate:results2metadata: Unexpected number of mwemetas: {len(mwemetas)}\n{str(mwemetas)}', file=sys.stderr)
    if len(mwemetas) == 0:
        result = None
        #    result = MWEMeta(sentence, sentenceid, origutt, mwelexicon, mlq, '', [], -1, 'UNK', 'NO') # dit moet uit staan!!!
    return result


def getmajorlemmaqueries(lemmanodes: List[SynTree]) -> List[XpathExpression]:
    results = [
        f'.//node[{expandaltvals("@lemma", getattval(lemmanode, "lemma"), "=")}]'
        for lemmanode in lemmanodes
    ]
    return results


def noduplicatesin(lst: list) -> bool:
    seenelements = []
    for el in lst:
        if el in seenelements:
            return False
        else:
            seenelements.append(el)
    return True


def expandlemmas(lemmas: List[str]) -> List[List[str]]:
    results = []
    if lemmas == []:
        return [[]]
    head = lemmas[0]
    tail = lemmas[1:]
    altheads = head.split(altsym)
    tailresults = expandlemmas(tail)
    for althead in altheads:
        for tailresult in tailresults:
            result = [althead] + tailresult
            results.append(result)
    return results


def identicalisin(mwemeta: MWEMeta, mwemetalist: List[MWEMeta]) -> bool:
    for lmwemeta in mwemetalist:
        if isidentical(mwemeta, lmwemeta):
            return True
    return False


def cleanmwemetalist(mwemetalist: List[MWEMeta]) -> List[MWEMeta]:
    """
    remove duplicates and occurrence with [] for positions if there are with non-empty positions
    :param mwemetalist:  mwemetalist with duplicates and [] positions
    :return: mwemetalist without duplicates and [][ positions if there are mwemetas with nonemptypositions
    """

    emptypositionslist = []
    resultlist = []
    for mwemeta in mwemetalist:
        if mwemeta is None:
            continue
        if mwemeta.positions == []:
            if not identicalisin(mwemeta, resultlist):
                emptypositionslist.append(mwemeta)
        elif not identicalisin(mwemeta, resultlist):
            resultlist.append(mwemeta)
    if resultlist == []:
        resultlist = emptypositionslist
    return resultlist


def getmwecomponentnodes(mwetree: SynTree) -> List[SynTree]:
    mwecomponents = mwetree.xpath(mwecomponentsxpath)
    return mwecomponents


def containsalllemmas(lemmaslist1: List[List[str]], lemmaslist2: List[List[str]]):
    zippedlemmaslists = zip(lemmaslist1, lemmaslist2)
    for lemmas1, lemmas2 in zippedlemmaslists:
        if any([lemma in lemmas2 for lemma in lemmas1]):
            pass
        else:
            return False
    return True


def annotate(  # noqa: C901
    syntree: SynTree, sentenceid: str
) -> Tuple[List[MWEMeta], List[MWEMeta], List[MWEMeta]]:
    discardedmwemetalist = []
    duplicatemwemetalist = []
    # get the lemmas from this tree
    rawlemmas = getlemmas(syntree)
    lemmas = adaptlemmas(rawlemmas)

    alllemmaslist = [rawlemmas, lemmas] if lemmas != rawlemmas else [rawlemmas]

    validmweids = []
    for lemmas in alllemmaslist:
        # for each lemma find the potential mwes
        for lemma in lemmas:
            if lemma in indexes.lemma2iddict:
                mweids = indexes.lemma2iddict[lemma]
            else:
                mweids = []

            # check for each mweid whether all lemmas it requires occurs in lemmas, if sp add it to validmweids
            for mweid in mweids:
                try:
                    mweidlemmas = indexes.lemmasofmwedict[str(mweid)]
                except KeyError as e:
                    print(f"{e}", file=sys.stderr)
                    print(indexes.id2mweid[str(mweid)], file=sys.stderr)
                    raise (KeyError)
                expandedmweidlemmaslist = expandlemmas(mweidlemmas)
                for expandedmweidlemmas in expandedmweidlemmaslist:
                    if is_subset(expandedmweidlemmas, lemmas):
                        if mweid not in validmweids:
                            validmweids.append(mweid)

    showsyntree = False
    if showsyntree:
        etree.dump(syntree)
    expandedsyntree = expandfull(syntree)
    showexpandedsyntree = False
    if showexpandedsyntree:
        etree.dump(expandedsyntree)
    sentence = getsentence(syntree)

    if sentence is None:
        raise RuntimeError(f"No sentence for tree {sentenceid}")

    mwemetalist = []

    # find the Alpino MWEs
    mwemetalist += getalpinomwes(expandedsyntree, sentenceid=sentenceid)

    for validmweid in validmweids:

        # find the mwe structure
        if (
            validmweid not in indexes.mwetreesdict
        ):  # this can happen if there duplicates
            continue
        mwetree = indexes.mwetreesdict[validmweid]
        origutt = getatt(mwetree, "origutt")
        annotatedwords = preprocess_MWE(origutt)
        annotations = [annotatedword[1] for annotatedword in annotatedwords]
        mwelexiconid = indexes.id2mweid[str(validmweid)]

        # get the mwestructures

        mwestructures = generatemwestructures(origutt, mwetree=mwetree)
        headpos = getmweheadpt(mwetree)
        mweheadposition = getmweheadposition(mwetree)
        mweheadlemma = getmweheadlemma(mwetree)

        showmwestructures = False
        if showmwestructures:
            for mwestructure in mwestructures:
                etree.dump(mwestructure)

        # determine the mweclasses and mwetype
        mwecomponentnodes = getmwecomponentnodes(mwestructures[0])
        mweclasses = getmweclasses(
            origutt, headpos, annotations, mweheadposition, mwecomponentnodes
        )
        # mwetype can only be computed when a match  has been found

        # derive the queries
        queries = generatequeries(origutt, mwetree=mwetree)

        # apply the mwe-query, get the components, and store the results
        mwequery = f".{queries[0]}"  # is the dot necessary?

        showexpandedsyntree = False
        if showexpandedsyntree:
            showtree(expandedsyntree, "mwe_annotate: annotate: expandedsyntree")
        # apply the mwequery
        try:
            mwequeryresults = expandedsyntree.xpath(mwequery)
        except etree.XPathEvalError as e:
            print(f"{e}, query=\n{mwequery}")
            mwequeryresults = []

        if mwequeryresults == []:
            # print(f'No mwe query results for {origutt}')
            mwelexid = indexes.id2mweid[str(validmweid)]
            if sentenceid == mwelexid:
                print(f"MEQ selfidentification failure ({mwelexid})")

        expandedmwestructureslist = [
            expandalternatives(mwestructure) for mwestructure in mwestructures
        ]
        altdebug = False
        if altdebug:
            print(
                "mwe_annotate: (altdebug): mwestructures with unexpanded alternatives"
            )
            for mwestructure in mwestructures:
                etree.dump(mwestructure)
            print("mwe_annotate: (altdebug):mwetrees with alternatives expanded")
        for expmwetrees in expandedmwestructureslist:
            if altdebug:
                for expmwetree in expmwetrees:
                    etree.dump(expmwetree)
            for mwequeryresult in mwequeryresults:
                mwetype = getmwetype(mwequeryresult, headpos, mweclasses)
                mwemeta = results2metadata(
                    mwequeryresult,
                    expmwetrees,
                    sentence,
                    sentenceid,
                    origutt,
                    mweclasses,
                    mwetype,
                    mwelexiconid,
                    meq,
                )
                if mwemeta is not None:
                    mwemetalist.append(mwemeta)

        # here we remove submwes from the mwemetalist and identify duplicates, and remove duplicates
        mwemetalist, discardedmwemetalist1, duplicatemwemetalist1 = removesubsetmwes(
            mwemetalist
        )
        mwemetalist, discardedmwemetalist2, duplicatemwemetalist2 = removeduplicatemwes(
            mwemetalist
        )
        discardedmwemetalist = discardedmwemetalist1 + discardedmwemetalist2

        nearmissqueryresults = []
        if mwequeryresults == []:
            nearmissquery = f".{queries[1]}"  # is the dot necessary?
            # apply the nearmissquery
            try:
                nearmissqueryresults = expandedsyntree.xpath(nearmissquery)
            except etree.XPathEvalError as e:
                print(f"{e}, query=\n{nearmissquery}")

            nearmissmwestructures = mknearmissstructs(mwestructures)
            for nearmissqueryresult in nearmissqueryresults:
                mwetype = getmwetype(nearmissqueryresult, headpos, mweclasses)
                mwemeta = results2metadata(
                    nearmissqueryresult,
                    nearmissmwestructures,
                    sentence,
                    sentenceid,
                    origutt,
                    mweclasses,
                    mwetype,
                    mwelexiconid,
                    nmq,
                )
                mwemetalist.append(mwemeta)

        if mwequeryresults == [] and nearmissqueryresults == []:
            querytype = mlq
            if queries[2] is not None:
                majorlemmaquery = f".{queries[2]}"
            else:
                majorlemmaquery = None
            mlqquerydebug = False
            if mlqquerydebug:
                print("mwe_annotate: mlqquerydebug")
                etree.dump(syntree)
                print(f"MLQ:\n{majorlemmaquery}")
            try:
                if majorlemmaquery is not None:
                    majorlemmaqueryresults = syntree.xpath(majorlemmaquery)
                else:
                    majorlemmaqueryresults = []
            except etree.XPathEvalError as e:
                print(f"{e}, query=\n{majorlemmaquery}")
                majorlemmaqueryresults = []

            for expandedmwestructures in expandedmwestructureslist:
                for (
                    mwetree
                ) in expandedmwestructures:  # was mwestructures but that was wrong
                    majorlemmas = getmajorlemmas(mwetree)
                    majorlemmaqueries = getmajorlemmaqueries(majorlemmas)
                    for majorlemmaqueryresult in majorlemmaqueryresults:
                        mwetype = getmwetype(None, headpos, mweclasses)
                        majorlemmanodeslist = []
                        for majorlemmaquery in majorlemmaqueries:
                            newmajorlemmanodes = majorlemmaqueryresult.xpath(
                                majorlemmaquery
                            )
                            if newmajorlemmanodes == []:
                                majorlemmanodeslist = (
                                    []
                                )  # all major lemmas must be present
                                break
                            else:
                                majorlemmanodeslist.append(newmajorlemmanodes)
                        majorlemmanodestuple = tuple(majorlemmanodeslist)
                        pd = itertools.product(*majorlemmanodestuple)
                        donepositions = []
                        for tpl in pd:
                            rawpositions = sorted(
                                [int(getattval(node, "end")) for node in tpl]
                            )
                            if rawpositions not in donepositions and noduplicatesin(
                                rawpositions
                            ):
                                positions = rawpositions
                                donepositions.append(rawpositions)

                                headposition = getmlqheadposition(tpl, mweheadlemma)

                                mwemeta = MWEMeta(
                                    sentence,
                                    sentenceid,
                                    origutt,
                                    mwelexicon,
                                    querytype,
                                    mwelexiconid,
                                    positions,
                                    headposition,
                                    headpos,
                                    mweclasses,
                                    mwetype,
                                )
                                mwemetalist.append(mwemeta)

    cleanmetalist = cleanmwemetalist(mwemetalist)

    return cleanmetalist, discardedmwemetalist, duplicatemwemetalist


def getmlqheadposition(nodes: Tuple[SynTree], lemma: str) -> int:
    if len(nodes) > 0:
        firstnode = nodes[0]
        result = int(getattval(firstnode, "end"))
    else:
        result = -1
    for node in nodes:
        if getattval(node, "lemma") == lemma:
            result = int(getattval(node, "end"))
            return result
    return result


def removesubsetmwes(
    mwemetalist: List[MWEMeta],
) -> Tuple[List[MWEMeta], List[MWEMeta], List[MWEMeta]]:
    """
    if two results meat1 and meta2 for the same sentence with status MEQ have the same head and the meta1.positions
    is a real subset of meta2,positions, then meta1 is a submwe of meta2, and meta2 is a supermwe of meta1.
    if a mwemeta is a submwe of any other mwemeta, it is added to the discardedmwemetas;
    else it added to the keptmwemetas

    We assume that this is checked per sentence, so that the number of comparisons remains small
    (otherwise, other datastructures (e.g. dict with sentenceid as key) might speed up the process)
    :param mwemetalist: list of mwemeta elements for identified occurrences of mwes
    :return: (keptmwemetas, discardedmwemetas)
    """

    keptmwemetas = []
    discardedmwemetas = []
    duplicatemwemetas = []
    if len(mwemetalist) < 2:
        keptmwemetas = mwemetalist
    else:
        for mwemeta1 in mwemetalist:
            if mwemeta1 is None:
                print("None mwemeta1 encountered", file=sys.stderr)
                continue
            supermwefound = False
            for mwemeta2 in mwemetalist:
                if mwemeta2 is None:
                    print("None mwemeta2 encountered", file=sys.stderr)
                    continue
                # VPCs should not be removed Guideline 6
                # https://parsemefr.lis-lab.fr/parseme-st-guidelines/1.1/?page=070_Annotation_management/005_Frequently_asked_questions#faq-more-1-categ
                if (
                    mwemeta1 is not None
                    and mwemeta2 is not None
                    and mwemeta1 != mwemeta2
                    and mwemeta1.sentenceid == mwemeta2.sentenceid
                    and mwemeta1.sentence == mwemeta2.sentence
                    and mwemeta1.mwequerytype == meq
                    and mwemeta2.mwequerytype == meq
                    and mwemeta1.headposition == mwemeta2.headposition
                    and all(
                        [
                            position in mwemeta2.positions
                            for position in mwemeta1.positions
                        ]
                    )
                    and (
                        len(mwemeta2.mweclasses) != 1
                        or mwemeta2.mweclasses[0] in {"VPC.full", "VPC.semi", "VPC"}
                    )
                    and mwemeta1.positions != mwemeta2.positions
                ):  # we assume that both are sorted
                    supermwefound = True
                    discardedmwemetas.append(mwemeta1)
                    break
                if (
                    mwemeta1 is not None
                    and mwemeta2 is not None
                    and mwemeta1 != mwemeta2
                    and mwemeta1.sentenceid == mwemeta2.sentenceid
                    and mwemeta1.sentence == mwemeta2.sentence
                    and mwemeta1.mwequerytype == meq
                    and mwemeta2.mwequerytype == meq
                    and mwemeta1.headposition == mwemeta2.headposition
                    and mwemeta1.positions == mwemeta2.positions
                    and mwemeta1.mweid != mwemeta2.mweid
                    and mwemeta2.sentenceid != mwemeta2.mweid
                ):
                    duplicatemwemetas.append(mwemeta2)
            if not supermwefound:
                keptmwemetas.append(mwemeta1)

    result = (keptmwemetas, discardedmwemetas, duplicatemwemetas)
    return result


def removeduplicatemwes(
    mwemetalist: List[MWEMeta],
) -> Tuple[List[MWEMeta], List[MWEMeta], List[MWEMeta]]:
    """
    Duplicate MWEs can arise due to different syntactic selection variants and due to Alpino, e.gg
    -if it has a multiword svp
    -if V+P is in DUCAME because P is ld but Alpino analyses it as pc

    for syntactic selection varinants we seelct the longest because i meets more requirements
    :param mwemetalist:
    :return:
    """
    keptmwemetas = []
    discardedmwemetas = []
    duplicatemwemetas = []
    if len(mwemetalist) < 2:
        keptmwemetas = mwemetalist
    mwemetapairs = combinations(mwemetalist, 2)
    for mwemeta1, mwemeta2 in mwemetapairs:
        if mwemeta1 is None:
            print("None mwemeta1 encountered", file=sys.stderr)
            continue
        if mwemeta2 is None:
            print("None mwemeta2 encountered", file=sys.stderr)
            continue
        if (
            mwemeta1 != mwemeta2
            and mwemeta1.positions == mwemeta2.positions
            and mwemeta1.sentenceid == mwemeta2.sentenceid
            and mwemeta1.sentence == mwemeta2.sentence
            and mwemeta1.mwequerytype == meq
            and mwemeta2.mwequerytype == meq
        ):
            if mwemeta1.mwelexicon.lower() == "alpino":
                discardedmwemetas.append(mwemeta1)
            elif mwemeta2.mwelexicon.lower() == "alpino":
                discardedmwemetas.append(mwemeta2)
            elif len(mwemeta1.mwe) > len(mwemeta2.mwe):
                discardedmwemetas.append(mwemeta2)
            else:
                discardedmwemetas.append(mwemeta1)
            duplicatemwemetas.append(mwemeta1)
            duplicatemwemetas.append(mwemeta2)
        else:
            # keptmwemetas.append(mwemeta1)
            # keptmwemetas.append(mwemeta2)
            pass
    keptmwemetas = [
        mwemeta for mwemeta in mwemetalist if mwemeta not in discardedmwemetas
    ]
    result = (keptmwemetas, discardedmwemetas, duplicatemwemetas)
    return result


def getmwemetacounts(
    mwemetas: List[MWEMeta], sentcount=None
) -> Tuple[List[str], List[List[Any]]]:
    meqselfcount = 0
    meqcount = 0
    nmqselfcount = 0
    nmqcount = 0
    mlqselfcount = 0
    mlqcount = 0
    selfcount = 0
    totalcount = len(mwemetas)
    sentenceids = set()

    for mwemeta in mwemetas:
        sentenceids.add(mwemeta.sentenceid)
        if mwemeta.sentenceid == mwemeta.mweid:
            selfcount += 1
        if mwemeta.mwequerytype == meq:
            meqcount += 1
            if mwemeta.sentenceid == mwemeta.mweid:
                meqselfcount += 1
        if mwemeta.mwequerytype == nmq:
            nmqcount += 1
            if mwemeta.sentenceid == mwemeta.mweid:
                nmqselfcount += 1
        if mwemeta.mwequerytype == mlq:
            mlqcount += 1
            if mwemeta.sentenceid == mwemeta.mweid:
                mlqselfcount += 1

    meqselfscore = meqselfcount / selfcount * 100 if selfcount != 0 else "NA"
    nmqselfscore = nmqselfcount / selfcount * 100 if selfcount != 0 else "NA"
    mlqselfscore = mlqselfcount / selfcount * 100 if selfcount != 0 else "NA"

    meqscore = meqcount / totalcount * 100 if totalcount != 0 else "NA"
    nmqscore = nmqcount / totalcount * 100 if totalcount != 0 else "NA"
    mlqscore = mlqcount / totalcount * 100 if totalcount != 0 else "NA"

    querycount = meqcount + nmqcount + mlqcount
    queryscore = querycount / totalcount * 100 if totalcount != 0 else "NA"
    queryselfcount = meqselfcount + nmqselfcount + mlqselfcount
    queryselfscore = (
        queryselfcount / len(sentenceids) * 100 if len(sentenceids) != 0 else "NA"
    )
    sentcountstr = str(sentcount if sentcount is not None else "no count")

    rows = cast(
        List[List[Any]],
        [
            ["meq", meqcount, meqscore, meqselfcount, meqselfscore],
            ["nmq", nmqcount, nmqscore, nmqselfcount, nmqselfscore],
            ["mlq", mlqcount, mlqscore, mlqselfcount, mlqselfscore],
            ["Queries", querycount, queryscore, queryselfcount, queryselfscore],
            ["Total", totalcount],
            ["Different sentences", len(sentenceids)],
            ["# sentences", sentcountstr],
        ],
    )
    header = ["Item", "Count", "Score", "Self count", "Self score"]

    result = (header, rows)
    return result
