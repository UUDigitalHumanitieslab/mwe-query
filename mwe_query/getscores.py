from mwemeta import MWEMeta
from typing import Any, Dict, List, Tuple
from sastadev.rpf1 import getevalscores
from sastadev.xlsx import mkworkbook

SentId = str

MWEDict = Dict[SentId, List[MWEMeta]]
RPF1 = Tuple[float, float, float]
SentIdRPF1 = Tuple[SentId, RPF1]


def is_samemwe(resmwe: MWEMeta, refmwe: MWEMeta) -> bool:

    # same positions ?
    resmwespan = set(resmwe.positions)
    refmwespan = set(refmwe.positions)

    result1 = resmwespan == refmwespan

    # same head?

    result2 = resmwe.headposition == refmwe.headposition

    result = result1 and result2

    return result


def is_samemwe_samelabel(resmwe: MWEMeta, refmwe: MWEMeta) -> bool:
    result1 = is_samemwe(resmwe, refmwe)
    result2 = resmwe.mwetype == refmwe.mwetype

    result = result1 and result2
    return result


def mwedict2countlist(mwedict) -> List[list]:
    resultlist = []
    for id in mwedict:
        count = len(mwedict[id])
        newresult = [id, count]
        resultlist.append(newresult)
    sortedresultlist = sorted(resultlist, key=lambda x: x[0])
    return sortedresultlist


def mwedict2xl(mwedict, outfullname):
    rows = mwedict2countlist(mwedict)

    headers = [['sentid', 'count']]
    wb = mkworkbook(outfullname, headers, rows, freeze_panes=(1, 0))
    wb.close()


def getintersection(objs1: List[Any], objs2: List[Any], idfunc=None) -> List[Any]:
    result = []
    for obj1 in objs1:
        for obj2 in objs2:
            if idfunc is None:
                if obj1 == obj2:
                    result.append(obj2)
            else:
                if idfunc(obj1, obj2):
                    result.append(obj2)
    return result


def getscores(resmwes: MWEDict, refmwes: MWEDict, idfunc=is_samemwe) -> Tuple[List[SentIdRPF1], RPF1]:
    sentidscores = []
    overallintersection = []
    for sentid in refmwes:
        refmwes_sentid = refmwes[sentid]
        if sentid in resmwes:
            resmwes_sentid = resmwes[sentid]
            intersection = getintersection(
                resmwes_sentid, refmwes_sentid, idfunc=idfunc)
            lintersection = len(intersection)
            sentidscore = getevalscores(
                len(resmwes_sentid), len(refmwes_sentid), lintersection)

            sentidscores.append((sentid, sentidscore, len(
                resmwes_sentid), len(refmwes_sentid), lintersection))
            overallintersection.extend(intersection)
        else:
            # print(f"Sentence {sentid} found in ref but not in results")
            sentidscore = getevalscores(0, len(refmwes_sentid), 0)
            sentidscores.append(
                (sentid, sentidscore, 0, len(refmwes_sentid), 0))

    for sentid in resmwes:
        resmwes_sentid = resmwes[sentid]
        if sentid not in refmwes:
            # print(f"Sentence {sentid} found in results but not in reference")
            sentidscore = getevalscores(len(resmwes_sentid), 0, 0)
            sentidscores.append(
                (sentid, sentidscore, len(resmwes_sentid), 0, 0))

    refmwescount = sum([len(refmwes[id]) for id in refmwes])
    resmwescount = sum([len(resmwes[id]) for id in resmwes])
    overallscore = getevalscores(
        resmwescount, refmwescount, len(overallintersection))

    # mwedict2xl(refmwes, 'refmwescountpersent.xlsx')
    # mwedict2xl(resmwes, 'resmwescountpersent.xlsx')

    sortedsentidscores = sorted(sentidscores, key=lambda x: x[0])
    result = (sortedsentidscores, overallscore)
    return result
