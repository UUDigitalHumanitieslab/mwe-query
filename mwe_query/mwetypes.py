"""
Module to compute mwe classes and Parseme/Unidive mwetype
It is a separate module to avoid mutual dependencies
"""

from typing import List, Optional, Tuple
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import (
    find1,
    getattval as gav,
    clausecats,
)
from annotations import lvcannotation2annotationcodedict, cia, oia
from lexicons import irvindeplexicon
from mwetyping import Mwetype
from mwus import get_mwuprops
from getmwecomponents import getmwecomponents
from findiav import findiav, findlvciavnode

# constants for LVC subclasses
DO = 'DO'
BE = 'BE'
BC = 'BC'
GT = 'GT'
GV = 'GV'
CBE = 'CBE'
CBC = 'CBC'
CST = 'CST'

# constants for MWE types

VID = 'VID'
IAV = 'IAV'
IRV = 'IRV'
VPCfull = 'VPC.full'
VPClight = 'VPC.semi'
VPCfullP = f'{VPCfull}-P'
VPCfullN = f'{VPCfull}-N'
VPCfullA = f'{VPCfull}-ADJ'
VPCfullBW = f'{VPCfull}-ADV'
VPClightP = f'{VPClight}-P'
VPClightN = f'{VPClight}-N'
VPClightA = f'{VPClight}-ADJ'
VPClightBW = f'{VPClight}-ADV'
VPCmaybelight = 'VPC.maybelight'
VPCVID = 'VPCVID'   # temporary value to distinguish real VIDs from VPC-caused VIDs
MVC = 'MVC'
LVC = 'LVC'
NIRV = 'NIRV'
IRVi = 'IRV.indep'
IRVd = 'IRV.dep'

LVCfull = 'LVC.full'
LVCcause = 'LVC.cause'
LVCGV = f'{LVC}.{GV}'

ADJID = 'AdjID'
ADVID = 'AdvID'
NID = 'NID'
PID = 'PID'
PRONID = 'PronID'
CID = 'CID'
UID = 'UID'

headrels = ['hd', 'crd']  # should come from sastadev

iavrels = ['pc', 'mod', 'ld', 'predc', 'predm', 'svp']

compoundsep = '_'

zichallexpression = '(@lemma="zich" or @lemma="me" or @lemmma="mij" or @lemma="je" or @lemma="ons")'


PosTag = str

lvcsubclasses = [DO, BE, BC, GT, GV, CBE, CBC, CST]
lvcmweclasses = [f'{LVC}.{sc}' for sc in lvcsubclasses]
verbalmweclasses = [VID, IAV, IRV, VPCfull, MVC, IRVi, IRVd,
                    NIRV, VPClight, NIRV] + lvcmweclasses + [LVCfull, LVCcause]

pt2idclass = {
    "n": NID,
    "adj": ADJID,
    "bw": ADVID,
    "vnw": PRONID,
    "ww": VID,
    "vz": PID,
    "vg": CID,
    "tw": NID,
    "tsw": NID,
    "let": NID,
    "lid": PRONID,
    "spec": NID,
}

modrels = ["predm", "mod", "app", "obcomp", "me"]


def vpcmap(vpc: str, pt: str) -> str:
    if pt == 'adj':
        result = f'{vpc}-ADJ'
    elif pt == 'bw':
        result = f'{vpc}-ADV'
    elif pt == 'n':
        result = f'{vpc}-N'
    elif pt == 'vz':
        result = f'{vpc}-P'
    else:
        result = f'{vpc}-?'
        print(f'Unknown pt for vpc {vpc}: pt={pt}')
    return result


def vpcclass2type(vpc: str) -> str:
    if vpc.startswith(VPCmaybelight):
        newvpc = VPCfull + vpc[len(VPCmaybelight):]
    else:
        newvpc = vpc
    if newvpc.endswith('-P') or vpc.endswith('-ADV'):
        hyphenpos = newvpc.find('-')
        result = newvpc[0:hyphenpos]
    elif newvpc.endswith('-ADJ') or newvpc.endswith('-N'):
        result = VPCVID
    else:
        result = newvpc
    return result


def isverbal(mweclasses) -> bool:
    for mweclass in mweclasses:
        if mweclass in verbalmweclasses or mweclass.startswith('LVC') or mweclass.startswith('VPC'):
            return True
    return False


def oldgetmweclasses(
    mwe: str,
    mwepos: str,
    annotations: List[int],
    headposition: int,
    mwecomponents: List[SynTree],
) -> List[str]:
    results = []
    cheadposition = headposition - 1 if headposition > 0 else headposition
    if mwepos in ["n"]:
        results.append(NID)
    elif mwepos in ["vnw"]:
        results.append(PRONID)
    elif mwepos in ["ww"]:
        headcomponent = mwecomponents[headposition]
        if headcomponent is not None and gav(headcomponent, 'positie') == 'prenom':
            results.append(ADJID)
        elif headcomponent is not None and gav(headcomponent, 'positie') == 'nom':
            results.append(NID)
        elif (
            cheadposition >= 0
            and annotations[cheadposition] in lvcannotation2annotationcodedict
        ):
            class_suffix = lvcannotation2annotationcodedict[annotations[cheadposition]]
            lvc_class = f"LVC.{class_suffix[:-1]}"
            results.append(lvc_class)
        elif ismvc(mwecomponents):
            results.append(MVC)
        else:
            results.append(VID)
    elif mwepos in ["adj"]:
        results.append(ADJID)
    elif mwepos in ["bw"]:
        results.append(ADVID)
    elif mwepos in ["vz"]:
        results.append(PID)
    elif mwepos in ["vg"]:
        results.append(CID)
    else:
        results.append(UID)  # unknown idiom
    return results


def getmweclasses(
    mwe: str,
    mwepos: str,
    annotations: List[int],
    headposition: int,
    mwecomponents: List[SynTree],
    match: SynTree,
    mwetrees: List[SynTree]
) -> List[Tuple[List[str], List[int]]]:
    matchcomponentslist = getmwecomponents([match], mwetrees)
    if matchcomponentslist == []:
        return []
    else:
        if len(matchcomponentslist) > 1:
            print(
                f'getmwecomponetns:getmwecomponents: multiple matchcomponents found for <{mwe}>')
    matchcomponents = matchcomponentslist[0]
    allpositions = [getposition(n) for n in matchcomponents]
    headmatchcomponents = match.xpath('./node[@rel="hd" or @rel="crd"]')
    if headmatchcomponents == []:
        return []
    headmatchcomponent = headmatchcomponents[0]
    results = []
    classes = []
    # cheadposition = headposition - 1 if headposition > 0 else headposition
    if mwepos in ["n", "tw"]:
        classes.append("NID")
        newresult = (classes, allpositions)
        results.append(newresult)
    elif mwepos in ["vnw"]:
        classes.append("PronID")
        newresult = (classes, allpositions)
        results.append(newresult)
    elif mwepos in ["ww"]:
        if headmatchcomponent is not None and gav(headmatchcomponent, 'positie') == 'prenom':
            classes.append('AdjID')
            newresult = (classes, allpositions)
            results.append(newresult)
        elif headmatchcomponent is not None and gav(headmatchcomponent, 'positie') == 'nom':
            classes.append('NID')
            newresult = (classes, allpositions)
            results.append(newresult)
        else:
            mwetree = mwetrees[0]
            wwresults = getvclasses(match, mwetree, mwecomponents, annotations, headposition,
                                    headmatchcomponent, matchcomponents)
            results += wwresults
    elif mwepos in ["adj"]:
        classes.append("AdjID")
        newresult = (classes, allpositions)
        results.append(newresult)
    elif mwepos in ["bw"]:
        classes.append("AdvID")
        newresult = (classes, allpositions)
        results.append(newresult)

    elif mwepos in ["vz"]:
        classes.append("PID")
        newresult = (classes, allpositions)
        results.append(newresult)
    elif mwepos in ["vg"]:
        classes.append("CID")
        newresult = (classes, allpositions)
        results.append(newresult)
    else:
        classes.append("UID")  # unknown idiom
        newresult = (classes, allpositions)
        results.append(newresult)

    return results


def ismvc(mwecomponents: List[SynTree]) -> bool:
    result1 = all([gav(mwecomponent, "pt") ==
                  "ww" for mwecomponent in mwecomponents])
    results2 = (
        len(
            [
                mwecomponent
                for mwecomponent in mwecomponents
                if gav(mwecomponent, "wvorm") != "inf"
            ]
        )
        <= 1
    )
    result = result1 and results2
    return result


def getmwetype(
    mwematch: Optional[SynTree], mwepos: str, mweclasses: List[str]
) -> Mwetype:
    """
    compute the Parseme/Unidive MWE type
    :param mwepos:
    :param mweclasses:
    :return:
    """
    result = "NOID"
    if mwepos == "ww":
        if mweclasses == []:
            result = "NOID"
            # error message
        elif mweclasses == [NIRV]:
            result = IRV  # by including it in DUCAME it is considered an IRV
        elif len(mweclasses) >= 1:
            thelastclass = mweclasses[-1]
            lvc_classes = [
                mweclass for mweclass in mweclasses if mweclass.startswith(LVC)]
            if IRVd in mweclasses and IAV in mweclasses:
                result = VID
            elif (vpccontains(mweclasses, VPCfull) or vpccontains(mweclasses, VPClight)) and IAV in mweclasses:
                result = VID
            elif lvc_classes != [] and thelastclass not in [IAV]:
                if lvc_classes[0] == LVCGV:
                    result = LVCcause
                else:
                    result = LVCfull
            elif thelastclass == NIRV:
                result = VID   # maybe must also be IRV
            elif thelastclass in [IRVi]:
                result = IRV
            elif thelastclass in [VID, IAV, MVC]:
                result = thelastclass
            elif (thelastclass.startswith(VPCfull) or thelastclass.startswith(VPClight)) and \
                    vpcclass2type(thelastclass) is not None:
                result = vpcclass2type(thelastclass)
            elif thelastclass in {ADJID}:
                result = ADJID
            elif thelastclass in {NID}:
                result = NID          # maybe check for modifier rels to turn int into and AdvID

            else:
                result = UID
    else:  # if mwepos == "ww"
        if len(mweclasses) == 0:
            result = "NOID"
        elif len(mweclasses) >= 1:
            theclass = mweclasses[0]
            if theclass in ["NID", "PronID"]:
                mwerel = gav(mwematch, "rel") if mwematch is not None else ""
                if mwerel in modrels:
                    result = "AdvID"
                else:
                    result = theclass
            elif theclass in ["PID", "AdvID", "CID"]:
                result = "AdvId"
                # mwerel = gav(mwematch, "rel") if mwematch is not None else ""
                # if mwerel in {"mod", "predm", "me"}:
                #     result = "AdvID"
                # else:
                #     udheadlabel = getudheadlabel(mwematch)
                #     result = (
                #         pt2idclass[udheadlabel] if udheadlabel in pt2idclass else "UID"
                #     )
            elif theclass in ["AdjID"]:
                result = theclass
            else:
                result = theclass
    return result


def vpccontains(classes: List[str], vpc: str) -> bool:
    for aclass in classes:
        if aclass.startswith(vpc):
            return True
    return False


def getudheadlabel(stree: SynTree) -> PosTag:
    streecat = gav(stree, "cat")
    if streecat == "":
        result = gav(stree, "pt")
    elif streecat == "np":
        result = "n"
    elif streecat == "adjp":
        result = "adj"
    elif streecat == "advp":
        result = "bw"
    elif streecat == "pp":
        firstnonhead = getfirstchild(stree, lambda x: gav(x, "rel") != "hd")
        if firstnonhead is not None:
            result = getudheadlabel(firstnonhead)
        else:
            # should not happen
            result = "n"
    elif streecat == "mwu":
        headnode, pt, hdposition = get_mwuprops(stree)
        result = pt
    elif streecat in clausecats + ["ppres", "ppart"]:
        result = "ww"
    elif streecat == "conj":
        firstcnj = getfirstchild(stree, lambda x: gav(x, "rel") == "cnj")
        result = getudheadlabel(firstcnj)
    elif streecat == "detp":
        result = "vnw"
    elif streecat == "top":
        # should not happen
        result = getudheadlabel(stree[0])
    elif streecat in ["cat", "part"]:
        # should not happen
        result = "n"
    else:
        # should not happen; issue a warning
        result = "n"
    return result


def getfirstchild(stree: SynTree, f) -> Optional[SynTree]:
    for child in stree:
        if f(child):
            return child
    return None


def getvclasses(match: SynTree, mwetree: SynTree, mwecomponents: List[SynTree],
                annotations: List[int], headposition: int, match_hd: Optional[SynTree],
                mwematchcomponents: List[SynTree]) -> List[Tuple[List[str], List[int]]]:
    results = []
    classes = ()
    positions = ()
    coveredpositions = set()
    mwepositions = set(getposition(node) for node in mwematchcomponents)
    cheadposition = headposition - 1 if headposition > 0 else headposition

    if match_hd is not None:
        match_hdpt = gav(match_hd, 'pt')
        matchhdlemma = gav(match_hd, 'lemma')
        # matchhdword = gav(match_hd, 'word')
        match_hdposition = getposition(match_hd)
        positions = positions + (match_hdposition,)
        if match_hdpt == 'ww' and compoundsep in matchhdlemma:

            # find the svp
            lemmaparts = matchhdlemma.split(compoundsep)
            prtlemma = lemmaparts[0] if lemmaparts != [] else 'UNK'
            svpheads = match.xpath(
                f'./node[@rel="svp"]/node[@lemma="{prtlemma}"]')
            svphead = svpheads[0] if svpheads != [] else None
            if svphead is not None:
                svppt = gav(svphead, 'pt')
                svp_position = int(gav(svphead, 'end'))
                vpcclass = vpcmap(VPCfull, svppt)
                classes = classes + (vpcclass,)
                vpcpositions = (svp_position,)
                positions = positions + vpcpositions
                coveredpositions = coveredpositions.union(set(vpcpositions))
                newresult = (classes, positions)
                results.append(newresult)
            else:  # @@ does it still occur?
                coveredpositions = coveredpositions.union({match_hdposition})
                classes = classes + ('VPC.full',)
                newresult = (classes, positions)
                results.append(newresult)

        else:
            coveredpositions = coveredpositions.union({match_hdposition})

        semwenode = find1(mwetree, './node[@rel="se"]')
        sematchnode = find1(match, './node[@rel="se"]')
        if semwenode is not None and sematchnode is not None:
            if matchhdlemma in irvindeplexicon:
                if matchhdlemma in irvindeplexicon:
                    classes = classes + (IRVi,)
                else:
                    classes = classes + (IRVd,)
                seposition = getposition(sematchnode)
                positions = positions + (seposition,)
                coveredpositions.add(seposition)
                newresult = (classes, positions)
                results.append(newresult)

        zichobjmwenode = find1(
            mwetree, './node[@rel="obj1" and node[@rel="hd" and @lemma="me|mij|je|zich|ons"]]')
        zichobjmatchnode = find1(
            match, f'./node[@rel="obj1"]/node[@rel="hd" and {zichallexpression}]')

        if zichobjmwenode is not None and zichobjmatchnode is not None:
            if matchhdlemma in irvindeplexicon:
                classes = classes + ('NIRV',)
                seposition = getposition(zichobjmatchnode)
                positions = positions + (seposition,)
                coveredpositions.add(seposition)
                newresult = (classes, positions)
                results.append(newresult)

        iavfound = False
        iavposition = None
        iavmatchnode = findiav(mwetree, match)
        if iavmatchnode is not None:
            iavfound = True
            iavposition = getposition(iavmatchnode)
            coveredpositions.add(iavposition)

        # here add code for IAV's if found via OIA and CIA annotations
        if oia in annotations or cia in annotations:
            # add a condition to select the vz in the right position (i.e the one that has the cia/oia annotation
            iavmatchnode = findlvciavnode(mwetree, match)
            if iavmatchnode is not None:
                iavfound = True
                iavposition = getposition(iavmatchnode)
                coveredpositions.add(iavposition)

        # if any mwe positions are not covered yet, make them covered and add VID or LVC
        uncoveredpositions = {
            mweposition for mweposition in mwepositions if mweposition not in coveredpositions}
        if uncoveredpositions != set():
            if cheadposition >= 0 \
                    and annotations[cheadposition] in lvcannotation2annotationcodedict:
                class_suffix = lvcannotation2annotationcodedict[annotations[cheadposition]]
                lvc_class = f"LVC.{class_suffix[:-1]}"
                classes = classes + (lvc_class,)
                positions = positions + tuple(uncoveredpositions)
            elif ismvc(mwecomponents):
                classes = classes + ("MVC",)
                positions = positions + tuple(uncoveredpositions)
            else:
                classes = classes + ("VID",)
                positions = positions + tuple(uncoveredpositions)
            newresult = (classes, positions)
            results.append(newresult)

        # perhaps: make this combination without the IAV a separate MWE marking; yes we did this
        # for cases such een hekel hebben aan (* een hekel hebben)
        # then remove duplicates after the marking has been doen

        # after that add IAV to classes if iavfound = true
        if iavfound:
            classes = classes + (IAV,)
            positions = positions + (iavposition,)
            newresult = (classes, positions)
            results.append(newresult)

    listresults = [(list(classes), list(set(positions)))
                   for (classes, positions) in results]

    return listresults


def getposition(node):
    if 'end' in node.attrib:
        result = int(gav(node, 'end'))
    else:
        result = -1
    return result


def getcomponent(componentlist: List[SynTree], criterion) -> Optional[SynTree]:
    results = filter(criterion, componentlist)
    resultslist = list(results)
    if resultslist == []:
        return None
    else:
        return resultslist[0]
