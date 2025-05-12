from typing import Dict, List
from collections import defaultdict
from dataclasses import dataclass
from mycuptlib import MWE
from sastadev.xlsx import getxlsxdata

tab = "\t"
Mwetype = str
mwetypes = ["VID.full", "VID.semi", "VPC"]
FileName = str
SentId = str

mwemetaheader = [
    "sentence",
    "sentenceid",
    "mwe",
    "mwelexicon",
    "mwequerytype",
    "mweid",
    "positions",
    "headposition",
    "headpos",
    "headlemma",
    "mweclasses",
    "mwetype",
]

plussym = "+"
noval = "_"
comma = ","
initval = []

meq = "MEQ"
nmq = "NMQ"
mlq = "MLQ"
mlqcnvso = "MLQCNVSO"

meqcol = 3
nmqcol = meqcol + 1
mlqcol = nmqcol + 1

mweqt2col = {}
mweqt2col[meq] = meqcol
mweqt2col[nmq] = nmqcol
mweqt2col[mlq] = mlqcol
mweqt2col[mlqcnvso] = mlqcol

innersep = ";"


@dataclass
class MWEMeta:
    sentence: str
    sentenceid: str
    mwe: str
    mwelexicon: str
    mwequerytype: str
    mweid: str
    positions: list
    headposition: int
    headpos: str
    headlemma: str
    mweclasses: list
    mwetype: str

    def tocupt(self):
        pass

    def torow(self):
        sortedpositions = sorted(self.positions)
        mweclassesstr = plussym.join(self.mweclasses)
        result = [
            self.sentence,
            str(self.sentenceid),
            self.mwe,
            self.mwelexicon,
            self.mwequerytype,
            self.mweid,
            str(sortedpositions),
            str(self.headposition),
            self.headpos,
            self.headlemma,
            mweclassesstr,
            self.mwetype,
        ]
        return result


def fromrow(row: List[str]) -> MWEMeta:
    result = MWEMeta(row[0], row[1], row[2], row[3], row[4], row[5], str2intlist(row[6]),
                     int(row[7]), row[8], row[9], str2list(row[10], sep='+'), row[11])
    return result


def str2list(wrd: str, sep=comma) -> List[str]:
    strippedwrd = wrd.strip()
    if len(strippedwrd) >= 2 and strippedwrd[0] == '[' and strippedwrd[-1] == ']':
        barewrd = strippedwrd[1:-1]
    else:
        barewrd = strippedwrd
    rawresult = barewrd.split(sep)
    result = [res.strip() for res in rawresult]
    return result


sentencestr = 'sentence'
sentenceidstr = 'sentenceid'
mwestr = 'mwe'
mwelexiconstr = 'mwelexicon'
mwequerytypestr = 'mwequerytype'
mweidstr = 'mweid'
positionsstr = 'positions'
headpositionstr = 'headposition'
headposstr = 'headpos'
headlemmastr = 'headlemma'
mweclassesstr = 'mweclasses'
mwetypestr = 'mwetype'


def mwemeta2dict(mwemeta: MWEMeta, omit={}) -> dict:
    mwedict = {}
    if sentencestr not in omit:
        mwedict[sentencestr] = mwemeta.sentence
    if sentenceidstr not in omit:
        mwedict[sentenceidstr] = mwemeta.sentenceid
    if mwestr not in omit:
        mwedict[mwestr] = mwemeta.mwe
    if mwelexiconstr not in omit:
        mwedict[mwelexiconstr] = mwemeta.mwelexicon
    if mwequerytypestr not in omit:
        mwedict[mwequerytypestr] = mwemeta.mwequerytype
    if mweidstr not in omit:
        mwedict[mweidstr] = mwemeta.mweid
    if positionsstr not in omit:
        mwedict[positionsstr] = mwemeta.positions
    if headpositionstr not in omit:
        mwedict[headpositionstr] = mwemeta.headposition
    if headposstr not in omit:
        mwedict[headposstr] = mwemeta.headpos
    if headlemmastr not in omit:
        mwedict[headlemmastr] = mwemeta.headlemma
    if mweclassesstr not in omit:
        mwedict[mweclassesstr] = mwemeta.mweclasses
    if mwetypestr not in omit:
        mwedict[mwetypestr] = mwemeta.mwetype
    return mwedict


def str2intlist(wrd: str) -> List[int]:
    strlist = str2list(wrd)
    # if '' in strlist:
    #    print(wrd)
    result = [int(el) if el != '' else -1 for el in strlist]
    return result


def isidentical(mwemeta1: MWEMeta, mwemeta2: MWEMeta) -> bool:
    result = (
        mwemeta1.sentence == mwemeta2.sentence
        and mwemeta1.sentenceid == mwemeta2.sentenceid
        and mwemeta1.mwe == mwemeta2.mwe
        and mwemeta1.mwelexicon == mwemeta2.mwelexicon
        and mwemeta1.mwequerytype == mwemeta2.mwequerytype
        and mwemeta1.mweid == mwemeta2.mweid
        and sorted(mwemeta1.positions) == sorted(mwemeta2.positions)
        and mwemeta1.headposition == mwemeta2.headposition
        and mwemeta1.headpos == mwemeta2.headpos
        and mwemeta1.headlemma == mwemeta2.headlemma
        and sorted(mwemeta1.mweclasses) == sorted(mwemeta2.mweclasses)
        and mwemeta1.mwetype == mwemeta2.mwetype
    )

    return result


def metatoparsemetsv3(sentence: str, metas: List[MWEMeta]) -> str:
    tokens = sentence.split()
    rows = []
    for i, token in enumerate(tokens):
        position = i + 1
        row = [str(position), token, noval, initval, initval, initval]
        rows.append(row)

    newrows = rows
    for j, meta in enumerate(metas):
        if meta.positions != []:
            localid = j + 1
            firstposition = min(meta.positions)
            annotationcol = mweqt2col[meta.mwequerytype]
            for rowctr, newrow in enumerate(newrows):
                curposition = rowctr + 1
                if curposition == firstposition:  # self.headposition:
                    mweannotation = (
                        f"{localid}:{meta.mwetype}:{meta.mwelexicon}:{meta.mweid}"
                    )
                    newrow[annotationcol] = newrow[annotationcol] + \
                        [mweannotation]
                elif curposition in meta.positions:
                    mweannotation = f"{localid}"
                    newrow[annotationcol] = newrow[annotationcol] + \
                        [mweannotation]
                else:
                    # nothing has to change
                    pass

    finalrows = []
    for row in newrows:
        finalrow = row[:meqcol] + \
            [innersep.join(cell) for cell in row[meqcol:]]
        finalrow = adaptemptycells(finalrow)
        finalrows.append(finalrow)

    stringlist = [tab.join(row) for row in finalrows]
    resultstring = "\n".join(stringlist)

    return resultstring


def adaptemptycells(row: List[str]) -> List[str]:
    newrow = [noval if cell == "" else cell for cell in row]
    return newrow


def mkrow(annotation: str, mwequerytype) -> List[str]:
    if mwequerytype == meq:
        result = [annotation, noval, noval]
    elif mwequerytype == nmq:
        result = [noval, annotation, noval]
    elif mwequerytype == mlq:
        result = [noval, noval, annotation]
    else:
        result = []

    return result


def mwemeta2parseme_mwe(mwemeta: MWEMeta) -> MWE:
    mwe = MWE(mwemeta.mwetype, set(mwemeta.positions))
    return mwe


def getannotationfiles(afs: List[FileName], selection=[]) -> Dict[SentId, List[MWEMeta]]:
    resultdict = defaultdict(list)
    for af in afs:
        header, data = getxlsxdata(af)
        for row in data:
            mwemeta = fromrow(row)
            sentid = str(row[1])
            if selection != []:
                if sentid in selection:
                    resultdict[sentid].append(mwemeta)
            else:
                resultdict[sentid].append(mwemeta)
    return resultdict
