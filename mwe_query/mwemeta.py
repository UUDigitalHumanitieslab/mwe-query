from typing import List
from dataclasses import dataclass

tab = "\t"
Mwetype = str
mwetypes = ["VID.full", "VID.semi", "VPC"]

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
    "mweclasses",
    "mwetype",
]

plussym = "+"
noval = "_"
initval = []

meq = "MEQ"
nmq = "NMQ"
mlq = "MLQ"

meqcol = 3
nmqcol = meqcol + 1
mlqcol = nmqcol + 1

mweqt2col = {}
mweqt2col[meq] = meqcol
mweqt2col[nmq] = nmqcol
mweqt2col[mlq] = mlqcol

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
            mweclassesstr,
            self.mwetype,
        ]
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
                    newrow[annotationcol] = newrow[annotationcol] + [mweannotation]
                elif curposition in meta.positions:
                    mweannotation = f"{localid}"
                    newrow[annotationcol] = newrow[annotationcol] + [mweannotation]
                else:
                    # nothing has to change
                    pass

    finalrows = []
    for row in newrows:
        finalrow = row[:meqcol] + [innersep.join(cell) for cell in row[meqcol:]]
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

    return result
