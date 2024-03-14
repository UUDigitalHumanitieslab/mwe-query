"""
Module to compute mwe classes and Parseme/Unidive mwetype
It is a separate module to avoid mutual dependencies
"""

from typing import List, Optional
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import (
    getattval as gav,
    clausecats,
)
from .annotations import lvcannotation2annotationcodedict
from .mwetyping import Mwetype
from .mwus import get_mwuprops

PosTag = str

pt2idclass = {
    "n": "NID",
    "adj": "AdjID",
    "bw": "AdvID",
    "vnw": "PronID",
    "ww": "VID",
    "vz": "PID",
    "vg": "CID",
    "tw": "NID",
    "tsw": "NID",
    "let": "NID",
    "lid": "PronID",
    "spec": "NID",
}

modrels = ["predm", "mod", "app", "obcomp", "me"]


def getmweclasses(
    mwe: str,
    mwepos: str,
    annotations: List[int],
    headposition: int,
    mwecomponents: List[SynTree],
) -> List[str]:
    results = []
    cheadposition = headposition - 1 if headposition > 0 else headposition
    if mwepos in ["n"]:
        results.append("NID")
    elif mwepos in ["vnw"]:
        results.append("PronID")
    elif mwepos in ["ww"]:
        if (
            cheadposition >= 0
            and annotations[cheadposition] in lvcannotation2annotationcodedict
        ):
            class_suffix = lvcannotation2annotationcodedict[annotations[cheadposition]]
            lvc_class = f"LVC.{class_suffix[:-1]}"
            results.append(lvc_class)
        elif ismvc(mwecomponents):
            results.append("MVC")
        else:
            results.append("VID")
    elif mwepos in ["adj"]:
        results.append("AdjID")
    elif mwepos in ["bw"]:
        results.append("AdvID")
    elif mwepos in ["vz"]:
        results.append("PID")
    elif mwepos in ["vg"]:
        results.append("CID")
    else:
        results.append("UID")  # unknown idiom
    return results


def ismvc(mwecomponents: List[SynTree]) -> bool:
    result1 = all([gav(mwecomponent, "pt") == "ww" for mwecomponent in mwecomponents])
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
    :param mwe:
    :param mwepos:
    :param mweclasses:
    :return:
    """
    result = "NOID"
    if mwepos == "ww":
        if mweclasses == []:
            result = "NOID"
            # error message
        elif len(mweclasses) > 1:
            result = "VID"
        elif len(mweclasses) == 1:
            theclass = mweclasses[0]
            if theclass in ["VPC.full", "VPC.semi", "VID", "IAV", "IRV", "MVC"]:
                result = theclass
            elif theclass.startswith("LVC"):
                if theclass == "LVC.GV":
                    result = "LVC.cause"
                else:
                    result = "LVC.full"
            else:
                result = "UID"
    else:
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
                mwerel = gav(mwematch, "rel") if mwematch is not None else ""
                if mwerel in {"mod", "predm", "me"}:
                    result = "AdvID"
                else:
                    udheadlabel = getudheadlabel(mwematch)
                    result = (
                        pt2idclass[udheadlabel] if udheadlabel in pt2idclass else "UID"
                    )
            elif theclass in ["AdjID"]:
                result = theclass
            else:
                result = theclass
    return result


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
        result = getudheadlabel[stree[0]]
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
