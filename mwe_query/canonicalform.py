"""
Methods for parsing annotated canonical forms,
to generate queries from them and to search using these queries.
"""

from typing import cast, Dict, Iterable, List, Sequence, Optional, Set, Tuple, TypeVar
from sastadev.sastatypes import SynTree
import logging
import re
import sys
from .tbfstandin import getnodeyield
from .mwetyping import Annotation, Axis, NodeCondition, Polarity, Xpathexpression
from .mwuwordlemmas import reversemwuwordlemmadict
from .pronadvs import pronadvlemmas, Radpositions

from sastadev.treebankfunctions import (
    clausecats,
    getattval as gav,
    terminal,
    find1,
    bareindexnode,
    indextransform,
    getindexednodesmap,
    getbasicindexednodesmap,
    clausebodycats,
    showtree,
)

import lxml.etree as ET
import copy
from .adpositions import vzazindex
from .alternatives import expandalternatives
from sastadev.alpinoparsing import parse
from .annotations import (
    lvcannotationstrings,
    lvcannotationcode2annotationdict,
    lvcannotation2annotationcodedict,
)
from .annotations import (
    noann,
    modifiable,
    inflectable,
    modandinfl,
    variable,
    bound,
    dd,
    invariable,
    zero,
    com,
    literal,
    unmodifiable,
    unmodandinfl,
    dr,
    id,
    negpol,
    msem,
    lsem,
    lvc_lbt,
    inlsem,
    inmsem,
    coll,
)
from .lcat import expandnonheadwords
from .rwq import getrwqnode

log = logging.getLogger()

space = " "
underscore = "_"
compoundsep = underscore
DEBUG = False


altsym = "|"

alternativetag = "alternative"
alternativestag = "alternatives"


(
    start_state,
    invbl_state,
    dd_state,
    com_state,
    dr_state,
    id_state,
    inlsem_state,
    inmsem_state,
) = (0, 1, 2, 3, 4, 5, 6, 7)


notop, itop, parenttop = 0, 1, 2


mwstates = {invbl_state, dd_state, com_state, dr_state, inlsem_state, inmsem_state}
vblwords = ["iemand", "iets", "iemand|iets", "iets|iemand", "iemands", "ergens"]
boundprons = ["zich", "zijn", "zichzelf", "hij", "hem"]
modanns = {modifiable, modandinfl}
nomodanns = {unmodifiable, unmodandinfl, coll}

zichlemmas = ["me", "mij", "je", "zich", "ons"]
zichzelflemmas = ["mezelf", "mijzelf", "jezelf", "jouzelf", "zichzelf", "onszelf"]
zijnlemmas = ["mijn", "jouw", "zijn", "ons", "jullie", "je"]
hijlemmas = ["ik", "jij", "je", "hij", "ie", "wij", "we", "jullie", "zij", "ze"]
hemlemmas = [
    "mij",
    "me",
    "jou",
    "je",
    " hem",
    "'m",
    "ons",
    "jullie",
    "hen",
    "hun",
    "haar",
    "'r",
    "ze",
]
hijhemlemmas = hijlemmas + hemlemmas
defdets = {"de", "het", "deze", "die", "dit", "dat"}
defRpronouns = {"er", "hier", "daar"}
# indefdets = {'een', 'geen', } no convincing example yet geen haan kraaide ernaar allows only een/geen and
#                               requires negpol licensor

contentwordpts = ["adj", "n", "tw", "ww", "bw"]


parentisclausal = " or ".join([f'parent::node[@cat="{ccat}"]' for ccat in clausecats])

vblnode = """(not(@word) and not(@pt) and count(node)=0)"""
npmodppidxpath = """.//node[@cat="np" and
                node[@rel="mod" and @cat="pp" and not(node[@rel="pobj1"]) and not(node[@rel="vc"])] and
                ../node[@rel="hd" and @pt="ww"]]/@id"""

vobj1nodeidxpath = (
    f'.//node[@rel="obj1" and {vblnode} and ../node[@rel="hd" and @pt="ww"]]/@id'
)
vblppnodeidxpath = f'//node[@cat="pp" and node[@rel="obj1" and {vblnode}]]/@id'


coreproperties = ["rel", "pt", "cat", "lemma"]
# maybe make this dependent on the pt (nominal (getal inherent), verbal (getal niet inherent)
inherentinflproperties = ["wvorm", "pvtijd", "getal-n", "getal", "persoon", "graad"]
contextualinflproperties = ["positie", "pvagr", "buiging", "naamval", "npagr"]
inflproperties = inherentinflproperties + contextualinflproperties
subcatproperties = [
    "ntype",
    "genus",
    "numtype",
    "vwtype",
    "lwtype",
    "vztype",
    "conjtype",
    "spectype",
]

defaultinhinflvalues = {
    "wvorm": {"inf", "pv"},
    "pvtijd": {"tgw"},
    "getal-n": {""},
    "getal": {"ev"},
    "persoon": {"3"},
    "graad": {"basis"},
}

xpathproperties = ["axis"]

pobj1node = ET.Element("node", attrib={"rel": "pobj1", "pt": "vnw"})
vcnode = ET.Element("node", attrib={"rel": "vc"})

de_lw = ET.Element("node", attrib={"lemma": "de", "pt": "lw"})
het_lw = ET.Element("node", attrib={"lemma": "het", "pt": "lw"})
van_vz = ET.Element("node", attrib={"lemma": "van", "pt": "vz", "vztype": "init"})
dummymod = ET.Element(
    "node",
    attrib={"rel": "mod", "pt": "dummy", "begin": "0", "end": "0", "word": "dummy"},
)


def orconds(att: str, vals: List[str]) -> str:
    """Generates an OR xpath for this attribute and passed values

    Args:
        att (str): attribute key
        vals (List[str]): values, when empty "true" is returned

    Returns:
        str: xpath attribute query
    """

    condlist = [f'@{att}="{val}"' for val in vals]
    if len(condlist) > 1:
        result = " or ".join(condlist)
    elif len(condlist) == 1:
        result = condlist[0]
    else:
        result = "true"
    endresult = "(" + result + ")"
    return endresult


def alts(ls: Iterable[str]) -> str:
    result = altsym.join(ls)
    return result


clausebodycatalts = orconds("cat", clausebodycats)


def selectinherentproperties(node):
    result = []
    for att in node.attrib:
        if att in defaultinhinflvalues:
            nodeval = node.attrib[att]
            defvals = defaultinhinflvalues[att]
            if nodeval not in defvals:
                result.append(att)
    return result


def nodecopy(node):
    newnode = ET.Element("node")
    for att, val in node.attrib.items():
        newnode.attrib[att] = val
    return newnode


def tokenize(sentence):
    sentence = re.sub(r"([\.\,\;\?!\(\)\"\\\/])", r" \1 ", sentence)  # ':' removed
    sentence = re.sub(r"(\.\s+\.\s+\.)", r" ... ", sentence)
    sentence = re.sub(r"^\s*(.*?)\s*$", r"\1", sentence)
    sentence = re.sub(r"\s+", r" ", sentence)
    return sentence.split()


T = TypeVar("T")


def listofsets2setoflists(listofset: Iterable[Iterable[T]]) -> List[List[T]]:
    resultset: List[List[T]]
    if listofset == []:
        resultset = [[]]
    else:
        resultset = []
        head, *tail = listofset
        for el in head:
            tailresults = listofsets2setoflists(tail)
            for tailresult in tailresults:
                newresult = [el] + tailresult
                resultset.append(newresult)
    return resultset


def getwordstart(wrd: str) -> Tuple[int, bool]:
    openbracketfound = False
    obindex = wrd.find(":[")
    if obindex != -1:
        wordstart = obindex + 2
        openbracketfound = True
    else:
        cindex = wrd.find(":")
        if cindex != -1:
            wordstart = cindex + 1
        else:
            wordstart = 0
    return wordstart, openbracketfound


def preprocess_MWE(rawmwe: str) -> List[Tuple[str, int]]:  # noqa: C901
    """
    Splits the input MWE into a list of tokens and annotations

    Args:
        rawmwe (str): cannonical annotated MWE (might contain syntax)

    Returns:
        List[Tuple[int, str]]: annotated tokens
    """
    mwe = mwenormalise(rawmwe)
    can_form = tokenize(mwe)
    ann_list: List[Tuple[str, int]] = []
    state = start_state
    for word in can_form:
        wordstart, openbracketfound = getwordstart(word)
        if state in mwstates:
            newword, newann, state = mwstate(word, state)
        elif state == start_state:
            if word[0] == "<" and word[-1] == ">":
                newann = invariable
                newword = word[1:-1]
            elif word[0] == "0":
                newann = zero
                newword = word[1:]
            elif word[0] == "^":
                newann = negpol
                newword = word[1:]
            elif word.lower() in vblwords:
                newann = variable
                if word.lower().startswith("iemands"):
                    newword = "iemands"
                elif word.lower().startswith("iemand"):
                    newword = "iemand"
                elif word.lower().startswith("iets"):
                    newword = "iets"
                else:
                    newword = word
            elif word.lower() in boundprons:
                newann = bound
                newword = word
            elif word == "<":
                state = invbl_state
                newann = noann
                newword = ""
            elif word[0] == "<":
                state = invbl_state
                newann = invariable
                newword = word[1:]
            elif word[:wordstart] in lvcannotationstrings and not openbracketfound:
                newann = lvcannotationcode2annotationdict[word[:wordstart]]
                newword = word[wordstart:]
            elif word[0:3].upper() == "L:[" and word[-1] == "]":
                newann = lsem
                newword = word[3:-1]
            elif word[0:3].upper() == "L:[" and word[-1] != "]":
                newann = inlsem
                state = inlsem_state
                newword = word[3:]
            elif word[0:2].upper() == "L:":
                newann = lsem
                newword = word[2:]
            elif word[0:2].lower() == "c:":
                newann = coll
                newword = word[2:]
            elif word[0:3].upper() == "M:[" and word[-1] == "]":
                newann = msem
                newword = word[3:-1]
            elif word[0:3].upper() == "M:[" and word[-1] != "]":
                newann = inmsem
                state = inmsem_state
                newword = word[3:]
            elif word[0:2].upper() == "M:":
                newann = msem
                newword = word[2:]
            elif word[0:4] == "dd:[" and word[-1] == "]":
                newann = dd
                newword = word[4:-1]
            elif word[0:4] == "dd:[" and word[-1] != "]":
                newann = dd
                state = dd_state
                newword = word[4:]
            elif word[0:4] == "id:[" and word[-1] == "]":
                newann = id
                newword = word[4:-1]
            elif word[0:4] == "id:[" and word[-1] != "]":
                newann = id
                state = id_state
                newword = word[4:]
            elif word[0:4] == "dr:[" and word[-1] == "]":
                newann = dr
                newword = word[4:-1]
            elif word[0:4] == "dr:[" and word[-1] != "]":
                newann = dr
                state = dr_state
                newword = word[4:]
            elif word[0:5] == "com:[" and word[-1] == "]":
                newann = com
                newword = word[5:-1]
            elif word[0:5] == "com:[" and word[-1] != "]":
                newann = com
                state = com_state
                newword = word[5:]
            elif word[0:2] in {"+*", "*+"}:
                newann = modandinfl
                newword = word[2:]
            elif word[0:2] in {"+#", "#+"}:
                newann = unmodandinfl
                newword = word[2:]
            elif word[0] == "*":
                newann = modifiable
                newword = word[1:]
            elif word[0] == "#" and len(word) > 1:
                newann = unmodifiable
                newword = word[1:]
            elif word[0] == "+":
                newann = inflectable
                newword = word[1:]
            elif word[0] == "=":
                newann = literal
                newword = word[1:]
            else:
                newann = noann
                newword = word
        else:
            log.debug('illegal state: %s for %s: mwe=%s', state, rawmwe, mwe)
            raise RuntimeError(f'illegal state: {state} for {rawmwe}')
        ann_list.append((newword, newann))

    return ann_list


def mwenormalise(rawmwe):
    result = rawmwe
    result = re.sub(r"(?i)iemand\s*\|\s*iets", "iemand|iets", result)
    result = re.sub(r"(?i)iets\s*\|\s*iemand", "iets|iemand", result)
    result = re.sub(r"<\s*", " <", result)
    result = re.sub(r"\s*>", "> ", result)
    result = space.join(result.split())
    return result


stateprops: Dict[int, Tuple[str, int]] = {}
stateprops[dd_state] = ("]", dd)
stateprops[dr_state] = ("]", dr)
stateprops[id_state] = ("]", id)
stateprops[inlsem_state] = ("]", inlsem)
stateprops[inmsem_state] = ("]", inmsem)
stateprops[com_state] = ("]", com)
stateprops[invbl_state] = (">", invariable)


def mwstate(word: str, instate: int) -> Tuple[str, int, int]:
    if word == stateprops[instate][0]:
        newstate = start_state
        newann = noann
        newword = ""
    elif word[-1] == stateprops[instate][0]:
        newstate = start_state
        newann = stateprops[instate][1]
        newword = word[:-1]
    else:
        newstate = instate
        newann = stateprops[instate][1]
        newword = word
    return (newword, newann, newstate)


def mincopynode(node: SynTree) -> SynTree:
    newnode = attcopy(node, ["rel", "pt", "cat"])
    return newnode


def mkresults(node, childslist):
    results = []
    for childs in childslist:
        newnode = nodecopy(node)
        for child in childs:
            newnode.append(child)
        results.append(newnode)
    return results


def getchild(stree: SynTree, rel: str) -> Optional[SynTree]:
    for child in stree:
        if gav(child, "rel") == rel:
            return child
    return None


def mknode():
    return ET.Element("node")


def all_leaves(
    stree: SynTree, annotations: List[Annotation], allowedannotations: Set[Annotation]
) -> bool:
    leaves = getnodeyield(stree)
    for leave in leaves:
        beginint = int(gav(leave, "begin"))
        if annotations[beginint] not in allowedannotations:
            return False
    return True


def headmodifiable(stree: SynTree, mwetop: int, annotations: List[int]):
    head = getchild(stree, "hd")
    if head is None:
        return False
    elif terminal(head):
        beginint = int(gav(head, "begin"))
        if 0 <= beginint < len(annotations):
            if mwetop == notop:
                result = annotations[beginint] in modanns
            elif mwetop in {itop, parenttop}:
                result = annotations[beginint] not in nomodanns
            else:
                log.warning('Illegal value for mwetop=%s', mwetop)
                result = False
        else:
            log.warning(f'Index out of range: {beginint} in {annotations}')
            result = False
    else:  # can now only be node with cat=mwu
        mwps = getnodeyield(head)
        if mwetop == notop:
            result = any(
                [annotations[int(gav(mwp, "begin"))] in modanns for mwp in mwps]
            )
        elif mwetop in {itop, parenttop}:
            result = any(
                [annotations[int(gav(mwp, "begin"))] not in nomodanns for mwp in mwps]
            )
        else:
            log.warning('Illegal value for mwetop=%s', mwetop)
            result = False
    return result


def attcopy(sourcenode: SynTree, atts: List[str]) -> SynTree:
    targetnode = mknode()
    # we always copy the 'id' and 'index'attributes, needed for conditions, perhaps not needed anymorre
    extatts = atts + ["id", "index"]
    for att in extatts:
        if att in sourcenode.attrib:
            if att == "word":
                targetnode.attrib[att] = sourcenode.attrib[att].lower()
            else:
                targetnode.attrib[att] = sourcenode.attrib[att]
    return targetnode


def zerochildrencount(stree, annotations):
    result = 0
    for child in stree:
        intbegin = int(child.attrib["begin"])
        if terminal(child):
            if 0 <= intbegin < len(annotations):
                if annotations[intbegin] == zero:
                    result += 1
            else:
                log.warning('Index out of range: %d in %s', intbegin, annotations)
    return result


def mknewnode(
    stree: SynTree, mwetop: int, atts: List[str], annotations: List[int]
) -> SynTree:
    newnode = attcopy(stree, atts)
    if not headmodifiable(stree, mwetop, annotations):
        if zerochildrencount(stree, annotations) == 0:
            newnode.attrib["nodecount"] = f"{len(stree)}"
        else:
            newnode.attrib["maxnodecount"] = f"{len(stree)}"
    return newnode


def expandnonheadwordnode(nonheadwordnode, phrasenodeproperties):
    phraserel = gav(nonheadwordnode, "rel")
    newnonheadwordnode = copy.copy(nonheadwordnode)
    newnonheadwordnode.attrib["rel"] = "hd"
    phrasenode = ET.Element("node", attrib=phrasenodeproperties)
    phrasenode.attrib["rel"] = phraserel
    phrasenode.append(newnonheadwordnode)
    return phrasenode


def zullenheadclause(stree: SynTree) -> bool:
    if stree.tag == "node":
        cat = gav(stree, "cat")
        head = getchild(stree, "hd")
        if head is None:
            return False
        headlemma = gav(head, "lemma")
        headpt = gav(head, "pt")
        result = cat in {"smain", "sv1"} and headlemma == "zullen" and headpt == "ww"
    else:
        result = False
    return result


# # what must happen to nodes in a tree
# #
# * nonterminal node:
#   * top node: remove node - if more than 1 child error
#   * highest sentential node with not zullen as head (smain: keep node no properties (or only @cat)
#   * highest sentential node with zullen as head: copy subject to subject of infinitive, delete subject, zullen
#   * vc node, top->  drop all  features
#   * nonterminal with only invariables as leaves: drop all children, keep rel
#   * nonterminal with only com and variable as leaves: 2 alternatives: (1) drop completely or treat normally
#   * other nonterminal node: drop all features except cat and rel, if head not modifiable add count(node) restrictions
# * terminal nodes
#   * noann:
#     * if head of the expression: keep lemma, pt, rel
#     * otherwise: word = node.@word.lower(), keep pt, rel
#   * modifiable: word = node.@word.lower(), keep pt, rel
#   * inflectable: keep lemma  pt, rel
#   * modandinfl: keep lemma  pt, rel
#   * variable: keep rel, drop children, for iemands naamval=gen
#   * bound
#     * zich: me, je , ons, je, mij,
#     * zichzelf mijzelf mezelf, jezelf, onszelf,
#     * zijn: if @pt=vnw-bez: mijn jouw, zijn haar,
#   * dd: @lemma in defdets
#   * invariable|: skip
#   * zero: if rel!= hd: delete node, else error
#   * com: keep lemma, pt, rel
#   * literal: word=node.@word.lower(), pt, rel


def persproadapt(node: SynTree) -> SynTree:
    if "genus" in node.attrib:
        del node.attrib["genus"]
    if "getal" in node.attrib:
        del node.attrib["getal"]
    if "persoon" in node.attrib:
        del node.attrib["persoon"]
    if "naamval" in node.attrib:
        del node.attrib["naamval"]
    if "status" in node.attrib:
        del node.attrib["status"]
    return node


def transformtree(  # noqa: C901
    stree: SynTree, annotations: List[Annotation], mwetop=notop, axis=None
) -> Sequence[Optional[SynTree]]:
    # it is presupposed that with zullen + vc the subject index node of the vc has already been expanded
    # it is presupposed that the function is called with node SynTree at the top
    if stree.tag != "node":
        return [stree]
    else:
        newnodes: List[Optional[SynTree]] = []
        if not terminal(stree):
            cat = gav(stree, "cat")
            rel = gav(stree, "rel")
            if cat == "top" and len(stree) > 1:

                newnode = mincopynode(stree)
                if axis is not None:
                    newnode.attrib["axis"] = axis
                newnodes.append(newnode)
            elif cat == "top" and len(stree) == 1:
                child = stree[0]
                results = transformtree(child, annotations, mwetop=itop)
                return results
            elif cat in {"smain", "sv1"}:
                head = getchild(stree, "hd")
                if head is None:
                    return []
                lemma = gav(head, "lemma")
                vc = getchild(stree, "vc")
                # predm, if present,  must be moved downwards here
                newstree = lowerpredm(stree)
                # print('newstree')
                # ET.dump(newstree)
                if lemma == "zullen" and vc is not None:
                    subject = find1(newstree, './node[@rel="su"]')
                    newvc = getchild(newstree, "vc")
                    if not isinstance(newvc, SynTree):
                        # TODO: correct behavior??
                        return []
                    newvc = expandsu(newvc, subject)
                    results = transformtree(newvc, annotations, mwetop=itop, axis=axis)
                    return results
                elif mwetop == itop:
                    newnode = ET.Element("node")
                    if axis is not None:
                        newnode.attrib["axis"] = axis
                    newnodes.append(newnode)
                else:
                    newnode = mincopynode(stree)
                    if axis is not None:
                        newnode.attrib["axis"] = axis
                    newnodes.append(newnode)
            elif rel == "vc" and mwetop == itop:
                atts: List[str] = []
                newnode = mknewnode(stree, mwetop, atts, annotations)
                if axis is not None:
                    newnode.attrib["axis"] = axis
                newnodes.append(newnode)
            elif all_leaves(stree, annotations, {invariable}):
                newnode = attcopy(stree, [])
                newnode.attrib["rel"] = rel
                if axis is not None:
                    newnode.attrib["axis"] = axis
                newnodes.append(newnode)
                return newnodes
            elif all_leaves(stree, annotations, {com}):
                newnode = attcopy(stree, ["rel", "cat"])
                if axis is not None:
                    newnode.attrib["axis"] = axis
                newnodes.append(newnode)
                newnode = None  # comitative argument need not be present
                newnodes.append(newnode)
            elif all_leaves(stree, annotations, {variable}):
                newnode = ET.Element("node", attrib={"rel": rel})
                if axis is not None:
                    newnode.attrib["axis"] = axis
                newnodes.append(newnode)
                return newnodes
            elif all_leaves(stree, annotations, {zero}):
                newnode = None  # remove it
                # ???
                # if axis is not None:
                #     newnode.attrib['axis'] = axis
                newnodes.append(newnode)
                return newnodes
            elif all_leaves(stree, annotations, {negpol}):
                newnode = None  # remove it
                newnodes.append(newnode)
                return newnodes
            elif all_leaves(stree, annotations, {inlsem, inmsem}):
                newnode = mknewnode(stree, mwetop, ["cat", "rel"], annotations)
                if "nodecount" in newnode.attrib:
                    del newnode.attrib["nodecount"]
                newnodes.append(newnode)
            else:
                atts = ["cat"] if mwetop == itop else ["rel", "cat"]

                newnode = mknewnode(stree, mwetop, atts, annotations)
                if axis is not None:
                    newnode.attrib["axis"] = axis
                siblinghead = find1(stree, '../node[@rel="hd"]')
                siblingheadpt = gav(siblinghead, "pt")
                if siblingheadpt == "ww" and stree.attrib["rel"] in {
                    "pc",
                    "ld",
                    "mod",
                    "predc",
                    "svp",
                    "predm",
                }:
                    newnode.attrib["rel"] = "pc|ld|mod|predc|svp|predm"
                newnodes.append(newnode)

            newchildalternativeslist = []
            for child in stree:
                childaxis = None
                if mwetop == itop and gav(child, "rel") == "hd":
                    newmwetop = parenttop
                elif zullenheadclause(child):
                    newmwetop = parenttop
                    childaxis = "descendant"
                else:
                    newmwetop = notop
                newchildalternatives = transformtree(
                    child, annotations, mwetop=newmwetop, axis=childaxis
                )
                newchildalternativeslist.append(newchildalternatives)

            # list of alternative childs -> alternatives of childlists
            newchildlistalternatives = listofsets2setoflists(newchildalternativeslist)

            results = []
            for newnode in newnodes:
                if newnode is not None:
                    for newchildlist in newchildlistalternatives:
                        # we must make a new copy to obtain a new tree
                        newnodecopy = nodecopy(newnode)
                        for newchild in newchildlist:
                            if newchild is not None:
                                if DEBUG:
                                    log.debug('\nnewchild:')
                                    ET.dump(newchild)
                                # we must make a copy of the child because each Element has only one parent
                                newchildcopy = copy.copy(newchild)
                                newnodecopy.append(newchildcopy)
                                if DEBUG:
                                    log.debug('\n\nnewnodecopy:')
                                    ET.dump(newnodecopy)
                        results.append(newnodecopy)
                else:
                    results.append(newnode)
        elif bareindexnode(stree):
            newnode = nodecopy(stree)  # delete @begin and @end here
            results = [newnode]

        elif terminal(stree):
            results = []
            beginint = int(gav(stree, "begin"))
            lcword = gav(stree, "word").lower()
            pt = gav(stree, "pt")
            rel = gav(stree, "rel")
            if not (0 <= beginint < len(annotations)):
                log.warning('Index out of range: %d in %s', beginint, annotations)
                # we simply skip this node
                # newnode = None
            else:
                # maybe something special if it concerns a head
                if annotations[beginint] == zero:
                    newnode = None
                    results.append(newnode)
                elif annotations[beginint] == negpol:
                    newnode = None
                    results.append(newnode)
                elif annotations[beginint] == literal:
                    newnode = attcopy(
                        stree,
                        ["lemma", "word", "rel", "pt"]
                        + subcatproperties
                        + inflproperties,
                    )
                    results.append(newnode)
                elif annotations[beginint] in {
                    inflectable,
                    modandinfl,
                    unmodandinfl,
                    lsem,
                    msem,
                    lvc_lbt,
                    coll,
                }:
                    newnode = attcopy(stree, ["lemma", "rel", "pt"] + subcatproperties)
                    results.append(newnode)
                elif (
                    annotations[beginint] in {noann, inlsem, inmsem}
                    or annotations[beginint] in lvcannotation2annotationcodedict
                ) and (mwetop != parenttop or rel != "hd"):
                    newnode = attcopy(
                        stree,
                        ["lemma", "rel", "pt"]
                        + subcatproperties
                        + inherentinflproperties,
                    )
                    results.append(newnode)
                elif (
                    (
                        annotations[beginint] in {noann, unmodifiable}
                        or annotations[beginint] in lvcannotation2annotationcodedict
                    )
                    and mwetop == parenttop
                    and rel == "hd"
                ):
                    selectedinherentinflproperties = selectinherentproperties(stree)
                    newnode = attcopy(
                        stree,
                        ["lemma", "rel", "pt"]
                        + subcatproperties
                        + selectedinherentinflproperties,
                    )
                    results.append(newnode)
                elif (
                    annotations[beginint] in {bound}
                    and lcword == "zijn"
                    and pt == "ww"
                    and (mwetop != parenttop or rel != "hd")
                ):
                    newnode = attcopy(
                        stree,
                        ["lemma", "rel", "pt"]
                        + subcatproperties
                        + inherentinflproperties,
                    )
                    results.append(newnode)
                elif (
                    annotations[beginint] in {bound}
                    and lcword == "zijn"
                    and pt == "ww"
                    and mwetop == parenttop
                    and rel == "hd"
                ):
                    newnode = attcopy(stree, ["lemma", "rel", "pt"] + subcatproperties)
                    results.append(newnode)
                elif annotations[beginint] in {com}:
                    newnode = attcopy(stree, ["lemma", "rel", "pt"] + subcatproperties)
                    results.append(newnode)
                elif annotations[beginint] in {modifiable, unmodifiable}:
                    newnode = attcopy(
                        stree,
                        ["lemma", "rel", "pt"]
                        + subcatproperties
                        + inherentinflproperties,
                    )
                    results.append(newnode)
                elif annotations[beginint] == variable:
                    newnode = attcopy(stree, ["rel"])
                    if gav(stree, "naamval") == "gen":
                        newnode.attrib["naamval"] = "gen"
                    results.append(newnode)
                elif annotations[beginint] == invariable:
                    newnode = attcopy(stree, ["rel"])
                    results.append(newnode)
                elif annotations[beginint] == bound:
                    newnode = attcopy(stree, ["rel", "pt"] + subcatproperties)
                    lemma = gav(stree, "lemma")
                    pt = gav(stree, "pt")
                    vwtype = gav(stree, "vwtype")
                    if lemma == "zich":
                        newnode.attrib["lemma"] = alts(zichlemmas)
                        newnode.attrib["vwtype"] = "refl|pr"
                    elif lemma == "zichzelf":
                        newnode.attrib["lemma"] = alts(zichzelflemmas)
                        newnode.attrib["vwtype"] = "refl|pr"
                    elif (
                        lemma == "zijn" and pt == "vnw" and vwtype == "bez"
                    ):  # we do not want to include the verb zijn here
                        newnode.attrib["lemma"] = alts(zijnlemmas)
                    elif lemma == "hij" and pt == "vnw" and vwtype == "pers":
                        newnode.attrib["lemma"] = alts(hijlemmas)
                        newnode.attrib["vwtype"] = "pers"
                        newnode = persproadapt(newnode)
                    elif lemma == "hem" and pt == "vnw" and vwtype == "pers":
                        newnode.attrib["lemma"] = alts(hemlemmas)
                        newnode.attrib["vwtype"] = "pers"
                        newnode = persproadapt(newnode)
                    results.append(newnode)
                elif annotations[beginint] == dd:
                    newnode = attcopy(stree, ["rel"])
                    newnode.attrib["lemma"] = alts(defdets)
                    newnode.attrib["pt"] = alts(["lw", "vnw"])
                    results.append(newnode)
                elif annotations[beginint] == dr:
                    newnode = attcopy(stree, ["rel"])
                    newnode.attrib["lemma"] = alts(defRpronouns)
                    newnode.attrib["pt"] = "vnw"
                    results.append(newnode)
                else:
                    log.warning('Unrecognized annotation: %s', annotations[beginint])
                    newnode = attcopy(
                        stree,
                        ["lemma", "rel", "pt"] + subcatproperties + inflproperties,
                    )
                    results.append(newnode)

        if DEBUG:
            log.debug('results:')
            for result in results:
                if result is None:
                    log.debug('None')
                else:
                    log.debug(ET.tostring(result))
        return results


def isvblnode(node: SynTree) -> bool:
    result = len(node) == 0 and "word" not in node.attrib and "pt" not in node.attrib
    return result


def expandsu(vc: SynTree, subject: SynTree) -> SynTree:
    """
    The function *expandsu* creates a copy of *vc* in which  the subject (su or sup) of *vc* has been replaced by *subject*,
    unless this subject is a variable subject
    :param vc:
    :param subject:
    :return:
    """
    newvc = copy.deepcopy(vc)
    newsubject: Optional[SynTree] = copy.deepcopy(subject)
    if subject is not None and isvblnode(subject):
        newsubject = None
    vcsup = find1(newvc, './node[@rel="sup"]')
    if vcsup is not None:
        vcsubject = vcsup
        if newsubject is not None:
            newsubject.attrib["rel"] = "sup"
    else:
        vcsubject = find1(newvc, './node[@rel="su"]')
    if vcsubject is not None and isvblnode(vcsubject) and newsubject is not None:
        newvc.remove(vcsubject)
        newvc.insert(0, newsubject)
    return newvc


def adaptvzlemma(lemma: str) -> str:
    if lemma == "met":
        result = "mee"
    elif lemma == " tot":
        result = " toe"
    else:
        result = lemma
    return result


def getpronadv(lemma, rel, rprons=set()):
    newnode = mknode()
    newlemma = adaptvzlemma(lemma)
    if rprons == set():
        rprons = {"er", "hier", "daar", "waar"}
    #        newnode.attrib['lemma'] = f'er{newlemma}|hier{newlemma}|daar{newlemma}|waar{newlemma}'
    newnode.attrib["lemma"] = alts([rpron + newlemma for rpron in rprons])
    if rel is not None:  # option needed for the supersetquery
        newnode.attrib["rel"] = rel
    newnode.attrib["pt"] = "bw"
    return newnode


def makepobj1vc(stree, obj1nodeid):
    results = []
    newstree = copy.deepcopy(stree)
    obj1node = find1(newstree, f'.//node[@id="{str(obj1nodeid)}"]')
    parent = obj1node.getparent()
    parent.remove(obj1node)
    newpobj1node = nodecopy(pobj1node)
    newvcnode = nodecopy(vcnode)
    parent.append(newpobj1node)
    parent.append(newvcnode)
    if "nodecount" in parent.attrib:
        parent.attrib["nodecount"] = str(len(parent))
    newresults = genvariants(newstree)
    results.append(newstree)
    results += newresults
    return results


def makevanPP(stree, gennodeid):
    results = []
    newstree = copy.deepcopy(stree)
    gennode = find1(newstree, f'.//node[@id="{str(gennodeid)}"]')
    parent = gennode.getparent()
    parent.remove(gennode)
    headnodegenus = find1(parent, './node[@rel="hd"]/@genus')
    headnodegetal = find1(parent, './node[@rel="hd"]/@getal')
    lw = (
        copy.copy(het_lw)
        if headnodegenus == "onz" and headnodegetal == "ev"
        else copy.copy(de_lw)
    )
    vanpp = ET.Element("node", attrib={"cat": "pp", "rel": "mod", "nodecount": "2"})
    van_vzcopy = copy.copy(van_vz)
    gennodecopy = attcopy(gennode, ["index", "id"])
    gennodecopy.attrib["rel"] = "obj1"
    vanpp.append(van_vzcopy)
    vanpp.append(gennodecopy)
    parent.append(lw)
    parent.append(vanpp)
    if "nodecount" in parent.attrib:
        parent.attrib["nodecount"] = str(len(parent))
    newresults = genvariants(newstree)
    results.append(newstree)
    results += newresults
    return results


def makenpzijn(stree, gennodeid):
    results = []
    newstree = copy.deepcopy(stree)
    gennode = find1(newstree, f'.//node[@id="{str(gennodeid)}"]')
    parent = gennode.getparent()
    parent.remove(gennode)
    detp = ET.Element("node", attrib={"rel": "det", "cat": "detp"})
    vbl = ET.Element("node", attrib={"rel": "mod"})
    bezvnw = ET.Element(
        "node",
        attrib={"rel": "hd", "lemma": "zijn|haar|hun", "pt": "vnw", "vwtype": "bez"},
    )
    detp.append(vbl)
    detp.append(bezvnw)
    parent.append(detp)
    newresults = genvariants(newstree)
    results.append(newstree)
    results += newresults
    return results


def mkpronadvvc(stree, ppnodeid):
    results = []
    newstree = copy.deepcopy(stree)
    ppnode = find1(newstree, f'.//node[@id="{str(ppnodeid)}"]')
    vzlemma = find1(ppnode, './/node[@rel="hd"]/@lemma')
    headnode = find1(ppnode, './node[@rel="hd"]')
    obj1node = find1(ppnode, './node[@rel="obj1"] ')
    if obj1node is not None and headnode is not None and vzlemma is not None:
        pronadvnode = getpronadv(vzlemma, "hd", rprons={"er"})
        newvcnode = nodecopy(vcnode)
        # print('ppnode:')
        # ET.dump(ppnode)
        ppnode.remove(headnode)
        ppnode.remove(obj1node)
        ppnode.append(pronadvnode)
        ppnode.append(newvcnode)
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def makepronadv(stree, ppnodeid):
    results = []
    newstree = copy.deepcopy(stree)
    ppnode = find1(newstree, f'.//node[@id="{str(ppnodeid)}"]')
    parent = ppnode.getparent()
    vzlemma = find1(ppnode, './/node[@rel="hd"]/@lemma')
    if vzlemma is not None:
        pprel = gav(ppnode, "rel")
        pronadv = getpronadv(vzlemma, pprel)
        parent.remove(ppnode)
        parent.append(pronadv)
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def mkextraobcomp(stree, obcompphraseid):
    results = []
    newstree = copy.deepcopy(stree)
    obcompphrase = find1(newstree, f'.//node[@id="{obcompphraseid}"]')
    obcomp = find1(obcompphrase, './/node[@rel="obcomp"]')
    streehead = find1(newstree, './node[@rel="hd"]')
    streeheadpt = gav(streehead, "pt")
    newtopnode = ET.Element("node")
    obcompphrase.remove(obcomp)
    # ET.dump(obcompphrase)
    obcomphead = find1(obcomp, './node[@rel="cmp"]')
    if (
        obcomphead is not None
        and obcomphead.attrib["lemma"] == "als"
        and obcomphead.attrib["pt"] == "vg"
    ):
        obcomphead.attrib["pt"] = "vz"
        obcomphead.attrib["vztype"] = "init"
        del obcomphead.attrib["conjtype"]

    ocpchilds = [child for child in obcompphrase]
    if len(ocpchilds) == 1:
        thechild = ocpchilds[0]
        thechild.attrib["rel"] = gav(obcompphrase, "rel")
        newobcompphrase = thechild
        # ET.dump(newobcompphrase)
    else:
        newobcompphrase = obcompphrase
    obcomp.attrib["rel"] = "predm|mod"
    if streeheadpt == "ww":
        newstree.append(obcomp)
        result = newstree
        newresults = genvariants(result)
    else:
        ocpparent = obcompphrase.getparent()
        ocpparent.remove(obcompphrase)
        ocpparent.append(newobcompphrase)
        newtopnode.append(ocpparent)
        newtopnode.append(obcomp)
        result = newtopnode
        newresults = []
    results += newresults
    results.append(result)

    return results


def makeppnp(stree, npmodppid):
    results = []
    newstree = copy.deepcopy(stree)
    npnode = find1(newstree, f'.//node[@id="{str(npmodppid)}"]')
    ppnode = find1(npnode, './node[@rel="mod" and @cat="pp" ]')
    if npnode is not None and ppnode is not None:
        newppnode = copy.deepcopy(ppnode)
        newppnode.attrib["rel"] = "mod|pc"
        npnode.remove(ppnode)
        if "nodecount" in npnode.attrib:
            npnode.attrib["nodecount"] = str(len(npnode))
        # ET.dump(newstree)
        npparent = npnode.getparent()
        npparent.append(newppnode)
        if "nodecount" in npparent.attrib:
            npparent.attrib["nodecount"] = str(len(npparent))
        # ET.dump(newstree)
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def makesubjectlessimperatives(stree, nodeid):
    results = []
    newstree = copy.deepcopy(stree)
    impnode = newstree if newstree.attrib["id"] == nodeid else None
    subject = find1(impnode, f'./node[@rel="su" and {vblnode} ]')
    head = find1(impnode, './node[@rel="hd" and @pt="ww"]')
    if impnode is not None and subject is not None:
        subject.attrib["presence"] = "no"
        impnode.attrib["cat"] = "sv1"
        head.attrib["wvorm"] = "pv"
        head.attrib["pvagr"] = "ev"
        head.attrib["pvtijd"] = "tgw"
        newresults = genvariants(newstree)
        results.append(newstree)
        results += newresults
    return results


def mkalternativesnode(altlists: List[List[SynTree]]) -> SynTree:
    """
    Creates alternatives nodes from the passed list
    """
    altnodes = [mkalternativenode(altlist) for altlist in altlists]
    alternativesnode = ET.Element(alternativestag)
    for altnode in altnodes:
        alternativesnode.append(altnode)
    return alternativesnode


def mkalternativenode(altlist: List[SynTree]) -> SynTree:
    alternativenode = ET.Element(alternativetag)
    for alt in altlist:
        if alt is not None:
            alternativenode.append(alt)
    return alternativenode


def finddeepestvc(stree: SynTree) -> Optional[SynTree]:
    for child in stree:
        childrel = gav(child, "rel")
        if childrel == "vc":
            result = finddeepestvc(child)
            return result
    streerel = gav(stree, "rel")
    if streerel == "vc":
        return stree
    else:
        return None


def lowerpredm(stree: SynTree) -> SynTree:
    # print('lowerpredm: stree:')
    # ET.dump(stree)
    newstree = copy.deepcopy(stree)
    predmxpath = f'.//node[@rel="predm" and ({parentisclausal})]'
    predmnodes = newstree.xpath(predmxpath)
    for predmnode in predmnodes:
        predmparent = predmnode.getparent()
        lowestvcnode = finddeepestvc(
            predmparent
        )  # this xpath does not yield the right results './/node[@rel="vc" and not(node[@rel="vc"])]')
        if lowestvcnode is not None:
            if predmparent is not None:
                predmparent.remove(predmnode)
                lowestvcnode.append(predmnode)
        # print('lowerpredm: newstree')
        # ET.dump(newstree)
    return newstree

    # genvariants2, different strategy, less multiplication


# 1. basic mwe structure, include predm, include subject
#  2. remove open slot subject (covers imperatives, topic drop, passives (in indexexpanded trees)
#  3. np[ ..pp] -> np pp
#  4. predm: & X dan ook predm .//node[@rel="vc" X and not(node[@rel="vc"])
#  5. local changes with alternatives and alternative nodes
#     a. obj1 -> pobj1 vc
#     b. vz obj1 -> vz pobj1 vc, advpron(vz) advpron(vz) + vc
#     c. gennodes
#     d. iemands


def newgenvariants(  # noqa: C901
    stree: SynTree, nodeidwordmap: Dict[int, str]
) -> List[SynTree]:
    results = []
    newstree = copy.deepcopy(stree)
    # remove open slot subject
    # maybe we should delete not all vbl subjects? //-> /
    vblsu = find1(newstree, f'.//node[@rel="su" and {vblnode}]')
    if vblsu is not None:
        parent = vblsu.getparent()
        if parent is not None:
            parent.remove(vblsu)

    # move predm down not needed already done in transformtree
    # newstree = lowerpredm(newstree)

    # Global changes
    globalresults = []
    # np[n mod/pp] -> np pc|mod/pp
    npmodppid = find1(stree, npmodppidxpath)
    if npmodppid is not None:
        ppnpresults = makeppnp(stree, npmodppid)
        globalresults += ppnpresults

    obcompphraseid = find1(stree, './/node[node[@rel="obcomp"]]/@id')
    if obcompphraseid is not None:
        obcompresults = mkextraobcomp(stree, obcompphraseid)
        globalresults += obcompresults

    globalresults.append(newstree)

    # local changes
    ppshow = False
    localresults = []
    for globalresult in globalresults:
        newstree = copy.deepcopy(globalresult)
        vobj1nodeids = globalresult.xpath(vobj1nodeidxpath)
        for vobj1nodeid in vobj1nodeids:
            obj1node = find1(newstree, f'//node[@id="{vobj1nodeid}"]')
            newpobj1node = nodecopy(pobj1node)
            newvcnode1 = nodecopy(vcnode)
            newvcnode2 = nodecopy(vcnode)
            parent = obj1node.getparent()
            if parent is not None:
                parent.remove(obj1node)
                alternativesnode = mkalternativesnode(
                    [[obj1node], [newvcnode1], [newpobj1node, newvcnode2]]
                )
                if ppshow:
                    showtree(alternativesnode, "alternativesnode")
                parent.append(alternativesnode)

        vblppnodeids = globalresult.xpath(vblppnodeidxpath)
        for vblppnodeid in vblppnodeids:
            ppnode = find1(newstree, f'//node[@id="{vblppnodeid}"]')
            newpobj1node1 = nodecopy(pobj1node)
            newpobj1phrasenode = expandnonheadwordnode(
                newpobj1node1, {"cat": "advp", "nodecount": "1"}
            )
            newvcnode1 = nodecopy(vcnode)
            newppnode1 = nodecopy(ppnode)
            newppnode1.attrib["nodecount"] = "3"
            parent = ppnode.getparent()
            if parent is not None:
                parent.remove(ppnode)
            vz = find1(ppnode, './node[@rel="hd" and @pt="vz"]')
            if vz is not None:
                newvz1 = copy.copy(vz)
                newvz1.attrib["vztype"] = "fin"
                pppobj1vcnode = newppnode1
                children = [newvz1, newpobj1phrasenode, newvcnode1]
                if any([child is None for child in children]):
                    pppobj1vcnode = None
                else:
                    for child in children:
                        pppobj1vcnode.append(child)
            else:
                pppobj1vcnode = None

            # pp with R-pronoun object
            if vz is not None:
                newppnode2 = copy.copy(ppnode)
                newvz2 = copy.copy(vz)
                newvz2.attrib["vztype"] = "fin"
                obj1node = find1(ppnode, './node[@rel="obj1"]')
                Rpronounobj1node = copy.copy(obj1node)
                # Rpronounobj1node.attrib['lemma'] = 'er|hier|daar|waar|ergens|nergens|overal' # not needed, actually wrong
                # Rpronounobj1node.attrib['pt'] = 'vnw' # not needed, actually wrong
                newphrase = expandnonheadwordnode(Rpronounobj1node, {})
                for child in newppnode2:
                    newppnode2.remove(child)
                newppnode2.append(newphrase)
                newppnode2.append(newvz2)
            else:
                newppnode2 = None

            # pp with R-pronoun object which has been replaced by a full NO with a dummymod
            if vz is not None:
                newppnode3 = copy.copy(ppnode)
                newvz3 = copy.copy(vz)
                newvz3.attrib["vztype"] = "fin"
                obj1node = find1(ppnode, './node[@rel="obj1"]')
                dummymodobj1node = copy.copy(obj1node)
                dummymodobj1node.attrib["cat"] = "np"
                dummymodobj1node.append(dummymod)
                for child in newppnode3:
                    newppnode3.remove(child)
                newppnode3.append(dummymodobj1node)
                newppnode3.append(newvz3)
            else:
                newppnode3 = None

            pppronadvvcnode = copy.copy(ppnode)
            for child in pppronadvvcnode:
                pppronadvvcnode.remove(child)
            if vz is not None:
                vzlemma = gav(vz, "lemma")
            if vz is not None and vzlemma != "":
                pronadvnode1 = getpronadv(vzlemma, "hd", rprons={"er"})
                newvcnode = nodecopy(vcnode)
                # print('ppnode:')
                # ET.dump(ppnode)
                pppronadvvcnode.append(pronadvnode1)
                pppronadvvcnode.append(newvcnode)

            # pp's with a pronominal adverb. e.g. daarnaar
            if vz is not None and vzlemma is not None:
                pprel = gav(ppnode, "rel")
                pronadvnode = getpronadv(vzlemma, pprel)
                pronadvppnode = expandnonheadwordnode(
                    pronadvnode, {"cat": "pp", "rel": pprel}
                )
                if ppshow:
                    showtree(pronadvppnode, "pronadvppnode1")
                # pronadvnode.attrib['rel'] = 'hd'   # this is superflous
                # pronadvppnode.append(pronadvnode)  # this is wrong, it adds a second one
                if ppshow:
                    showtree(pronadvppnode, "pronafvppnode2")

            else:
                pronadvppnode = None

            alternativesnode = mkalternativesnode(
                [
                    [ppnode],
                    [newppnode2],
                    [newppnode3],
                    [pppobj1vcnode],
                    [pppronadvvcnode],
                    [pronadvppnode],
                ]
            )
            if ppshow:
                showtree(alternativesnode, "alternativesnode2")
            if parent is not None:
                parent.append(alternativesnode)

        vblgennpnodeids = xpath_values(
            newstree,
            f'//node[@cat="np" and node[@naamval="gen" and @rel="det" and {vblnode}]]/@id',
        )
        for vblgennpnodeid in vblgennpnodeids:
            npnode = find1(newstree, f'//node[@id="{vblgennpnodeid}"]')
            detnode = find1(npnode, './node[@rel="det"]')
            # NP zijn etc
            detp = ET.Element("node", attrib={"rel": "det", "cat": "detp"})
            vbl = ET.Element("node", attrib={"rel": "mod"})
            bezvnw = ET.Element(
                "node",
                attrib={
                    "rel": "hd",
                    "lemma": "zijn|haar|hun",
                    "pt": "vnw",
                    "vwtype": "bez",
                },
            )
            detp.append(vbl)
            detp.append(bezvnw)
            npnode.remove(detnode)

            # de ... van X
            headnodegenus = find1(npnode, './node[@rel="hd"]/@genus')
            headnodegetal = find1(npnode, './node[@rel="hd"]/@getal')
            lwnode = (
                copy.copy(het_lw)
                if headnodegenus == "onz" and headnodegetal == "ev"
                else copy.copy(de_lw)
            )
            vanpp = ET.Element(
                "node", attrib={"cat": "pp", "rel": "mod", "nodecount": "2"}
            )
            van_vzcopy = copy.copy(van_vz)
            gennodecopy = attcopy(detnode, ["index", "id"])
            gennodecopy.attrib["rel"] = "obj1"
            vanpp.append(van_vzcopy)
            vanpp.append(gennodecopy)

            # Jans, tantes
            gendetnode = attcopy(detnode, ["index", "id", "naamval", "rel"])

            alternativesnode = mkalternativesnode(
                [[gendetnode], [detp], [lwnode, vanpp]]
            )
            npnode.append(alternativesnode)

        # past participle are sometimes adjectives
        showpparttrees = False
        if showpparttrees:
            showtree(newstree, "ppart: newstree:")
        ppartnodes = newstree.xpath('.//node[@cat="ppart"]')
        for ppartnode in ppartnodes:
            ppartparent = ppartnode.getparent()
            ppartnodecopy = copy.deepcopy(ppartnode)
            if showpparttrees:
                showtree(ppartnode, "ppart: ppartnode:")
            ppartheadnode = find1(ppartnode, './node[@rel="hd"]')
            if ppartheadnode is not None:
                apnode = attcopy(ppartnode, ["rel"])
                apnode.attrib["cat"] = "ap"
                for child in ppartnode:
                    if child == ppartheadnode:
                        newchild = attcopy(child, ["rel", "lemma"])
                        newchild.attrib["pt"] = "adj"
                        newchild.attrib["graad"] = "basis"
                        if "id" in child.attrib:
                            childid = child.attrib["id"]
                            origword = nodeidwordmap[childid]
                            newchild.attrib["lemma"] = getadjlemma(origword)
                    else:
                        newchild = copy.deepcopy(child)
                    apnode.append(newchild)
                alternativesnode = mkalternativesnode([[ppartnodecopy], [apnode]])
                if showpparttrees:
                    showtree(alternativesnode, "ppart: alternativesnode:")
                if ppartparent is not None:
                    ppartparent.remove(ppartnode)
                    ppartparent.append(alternativesnode)
                else:
                    newstree = alternativesnode
                if showpparttrees:
                    showtree(newstree, "ppart: modified newstree:")

        localresults.append(newstree)

    rawresults = localresults

    results = expandsvps(rawresults)

    return results


def getadjlemma(rawpastpart: str) -> str:
    # a bit ad-hoc; it will not work correctly for substantivised past participles
    pastpart = rawpastpart.lower()
    if pastpart.endswith("te") or pastpart.endswith("de") or pastpart.endswith("ne"):
        result = pastpart[:-1]
    else:
        result = pastpart
    return result


def genvariants(stree: SynTree) -> List[SynTree]:
    results = []
    # print('-->genvariants:')
    # ET.dump(stree)
    npmodppidxpath = f""".//node[@cat="np" and
                    node[@rel="mod" and @cat="pp" and node[{vblnode}] and not(node[@rel="pobj1"]) and not(node[@rel="vc"])] and
                    ../node[@rel="hd" and @pt="ww"]]/@id"""
    npmodppid = find1(stree, npmodppidxpath)

    obcompphraseid = find1(stree, './/node[node[@rel="obcomp"]]/@id')

    # np[n mod/pp] -> np pc|mod/pp
    if npmodppid is not None:
        ppnpresults = makeppnp(stree, npmodppid)
        results += ppnpresults

    # [zo .. obcomp/X] -> [[zo ..]  mod/X]  zo vrij als een vogel -> zo vrij [is] als een vogel
    if obcompphraseid is not None:
        obcompresults = mkextraobcomp(stree, obcompphraseid)
        results += obcompresults

    # print('<--genvariants')
    return results


def oldgenvariants(stree: SynTree) -> List[SynTree]:
    results = []

    # print('-->genvariants:')
    # ET.dump(stree)
    def catsv1(stree):
        return gav(stree, "cat") == "sv1"

    obj1nodeid = find1(stree, f'.//node[@rel="obj1" and {vblnode} ]/@id')
    ppnodeidxpath = f'.//node[@cat="pp" and node[@rel="hd"] and node[@rel="obj1" and {vblnode}] and count(node) =2]/@id'
    ppnodeid = find1(stree, ppnodeidxpath)
    gennodeid = find1(
        stree,
        './/node[@naamval="gen" and count(node)=0 and  not(@lemma) and not(@cat)]/@id',
    )
    npmodppidxpath = f""".//node[@cat="np" and
                    node[@rel="mod" and @cat="pp" and node[{vblnode}] and not(node[@rel="pobj1"]) and not(node[@rel="vc"])] and
                    ../node[@rel="hd" and @pt="ww"]]/@id"""
    npmodppid = find1(stree, npmodppidxpath)

    def hasvblsu(stree):
        return find1(stree, f'./node[@rel="su" and {vblnode}]') is not None

    def hasverbalhead(stree):
        return find1(stree, './node[@rel="hd" and @pt="ww"]') is not None

    if hasverbalhead(stree) and hasvblsu(stree) and gav(stree, "cat") != "sv1":
        potentialimperativenodeid = stree.attrib["id"]
    else:
        potentialimperativenodeid = None
    # potimpxpath = f'.//node[@cat="{alts(clausebodycats)}" and node[@rel="su" and {vblnode}]]/@id'
    # potentialimperativenodeid = find1(stree, potimpxpath)
    # pp[ vz obj1] -> pp[vz pobj1 vc (op iets -> er op dat....)
    # [ ..ww ... obj1 ] -> [
    if obj1nodeid is not None and not catsv1(stree):
        rvcresults = makepobj1vc(stree, obj1nodeid)
        results += rvcresults
    # pp[ vz obj1] -> bw  (pronominal adverb) naar iets -> ernaar/daarnaar etc
    if ppnodeid is not None and not catsv1(stree):
        pronadvresults = makepronadv(stree, ppnodeid)
        results += pronadvresults
    # pp[ vz obj1] -> pp[ hd/bw  (pronominal adverb) + vc/ ] op iets -> erop/ dat...
    if ppnodeid is not None and not catsv1(stree):
        pronadvvcresults = mkpronadvvc(stree, ppnodeid)
        results += pronadvvcresults
    # iemands n -> de/het n van iemand; iemand zijn/haar n
    if gennodeid is not None and not catsv1(stree):
        vanppresults = makevanPP(stree, gennodeid)
        results += vanppresults
        zijnnpresults = makenpzijn(stree, gennodeid)
        results += zijnnpresults

    # np[n mod/pp] -> np pc|mod/pp
    if npmodppid is not None and not catsv1(stree):
        ppnpresults = makeppnp(stree, npmodppid)
        results += ppnpresults

    # @@TODO: personal passives
    # @@TODO: impersonal passives
    # subjectless imperatives
    if potentialimperativenodeid is not None:
        subjectlessimperatives = makesubjectlessimperatives(
            stree, potentialimperativenodeid
        )
        results += subjectlessimperatives
    # print('<--genvariants')
    return results


def trees2xpath(strees: List[SynTree], expanded=False) -> Xpathexpression:
    if expanded:
        expandedstrees = [indextransform(stree) for stree in strees]
    else:
        expandedstrees = strees
    showthetree = False
    if showthetree:
        for i, stree in enumerate(expandedstrees):
            showtree(stree, f"{str(i)}:")
    xpaths = [tree2xpath(stree, 5) for stree in expandedstrees]
    if len(xpaths) == 1:
        finalresult = f"//{xpaths[0]}"
    else:
        result = " | ".join([f"\nself::{xpath}\n" for xpath in xpaths])
        finalresult = f"\n//node[{result}]"
    return finalresult


def corexpaths2xpath(xpaths: List[Xpathexpression]) -> Xpathexpression:
    if len(xpaths) == 1:
        finalresult = f"{xpaths[0]}"
    else:
        result = " | ".join([f"\nself::{xpath}\n" for xpath in xpaths])
        finalresult = f"\nnode[{result}]"
    return finalresult


def removesuperfluousindexes(stree: SynTree) -> SynTree:
    # ET.dump(stree)
    basicindexednodesmap = getbasicindexednodesmap(stree)
    # for ind, tree in basicindexednodesmap.items():
    #     print(ind)
    #     ET.dump(tree)
    indexnodesmap = getindexednodesmap(basicindexednodesmap)
    # for ind, tree in indexnodesmap.items():
    #    print(ind)
    #    ET.dump(tree)
    newstree = copy.deepcopy(stree)
    for node in newstree.iter():
        if "index" in node.attrib and node.attrib["index"] not in indexnodesmap:
            del node.attrib["index"]
    return newstree


def computeattconditionstr(stree) -> Tuple[NodeCondition, Polarity, Axis]:
    attconditions: List[str] = []
    polarity = "yes"
    axisstr = ""

    if stree.tag in ["node", "subnode", "localt"]:
        for att in stree.attrib:
            if att == "presence":
                if stree.attrib[att] == "no":
                    polarity = "no"
                continue
            if att in {"id", "index"}:
                continue
            elif att == "genus":  # nouns are not specified for genus when in plural
                genusval = str(stree.attrib["genus"])
                attcondition = f'(@genus="{genusval}" or @getal="mv")'
                attconditions.append(attcondition)
            elif att == "conditions":
                attcondition = str(stree.attrib[att])
                attconditions.append(attcondition)
            elif att == "nodecount":
                attstr = "count(node)"
                opstr = "="
                valint = int(stree.attrib[att])
                attcondition = f"{attstr}{opstr}{valint}"
                attconditions.append(attcondition)
            elif att == "maxnodecount":
                attstr = "count(node)"
                opstr = "<="
                valint = int(stree.attrib[att])
                attcondition = f"{attstr}{opstr}{valint}"
                attconditions.append(attcondition)
            elif att == "minnodecount":
                attstr = "count(node)"
                opstr = ">="
                valint = int(stree.attrib[att])
                attcondition = f"{attstr}{opstr}{valint}"
                attconditions.append(attcondition)
            elif att == "axis":
                if stree.attrib[att] is None:
                    axisstr = ""
                else:
                    axisstr = f"{str(stree.attrib[att])}::"
            else:
                attstr = f"@{str(att)}"
                opstr = "="
                val = stree.attrib[att]
                attcondition = expandaltvals(attstr, val, opstr)
                # vals = str(stree.attrib[att]).split('|')
                # if len(vals) == 1:
                #     val = str(stree.attrib[att])
                #     attcondition = f'{attstr}{opstr}"{val}"'
                # else:
                #     orconditionlist = [
                #         f'{attstr}{opstr}"{str(val)}"' for val in vals]
                #     attcondition = f'({" or ".join(orconditionlist)})'

                attconditions.append(attcondition)

        cleanattconditions = [
            attcondition for attcondition in attconditions if attcondition != ""
        ]
        attconditionstr = (
            f"({' and '.join(cleanattconditions)})" if cleanattconditions != [] else ""
        )

    return attconditionstr, polarity, axisstr


def tree2xpath(stree: SynTree, indent=0, indentstep=5) -> Xpathexpression:
    indentstr = indent * space
    realchilds = [
        child
        for child in stree
        if child.tag in ["node", "localt", "alternatives", "alternative"]
    ]
    childxpaths = [tree2xpath(child, indent + indentstep) for child in realchilds]
    if stree.tag == "localt":
        subnodechilds = [child for child in stree if child.tag == "subnode"]
        subnodechildtriples = [computeattconditionstr(child) for child in subnodechilds]
        subnodechildconditions = [
            subnodechildtriple[0] for subnodechildtriple in subnodechildtriples
        ]
        subnodesconditionstr = f"({' or '.join(subnodechildconditions)})"
        localtconditionstr, polarity, axisstr = computeattconditionstr(stree)
        attconditionstr = (
            f"({localtconditionstr} and {subnodesconditionstr})"
            if localtconditionstr != ""
            else subnodesconditionstr
        )

    if stree.tag == "node":
        attconditionstr, polarity, axisstr = computeattconditionstr(stree)

    if stree.tag in ["node", "localt"]:

        childxpathstr = (" and ").join(childxpaths)

        if attconditionstr == "" and childxpathstr == "":
            nodeconditions = []
        elif attconditionstr == "":
            nodeconditions = [childxpathstr]
        elif childxpathstr == "":
            nodeconditions = [attconditionstr]
        else:
            nodeconditions = [attconditionstr, childxpathstr]
        nodeconditionstr = " and ".join(nodeconditions)

        if nodeconditionstr == "":
            baseresult = f"{axisstr}node"
        else:
            baseresult = f"{axisstr}node[{nodeconditionstr}]"

        if polarity == "no":
            polresult = f"not({baseresult})"
        else:
            polresult = baseresult

        result = f"\n{indentstr}{polresult}"

    elif stree.tag == alternativestag:
        result = f"\n{indentstr}(" + " or ".join(childxpaths) + f"\n{indentstr})"

    elif stree.tag == alternativetag:
        result = f"\n{indentstr}(" + " and ".join(childxpaths) + f"\n{indentstr})"

    else:
        result = stree.tag
        # message that an illegal structure has been encountered

    return result


def expandaltvals(attstr, val, opstr):
    vals = val.split("|")
    if len(vals) == 1:
        val = vals[0]
        attcondition = f'{attstr}{opstr}"{val}"'
    else:
        orconditionlist = [f'{attstr}{opstr}"{str(val)}"' for val in vals]
        attcondition = f'({" or ".join(orconditionlist)})'
    return attcondition


def adaptindexes(stree: SynTree, antecedent: SynTree, rhdnode: SynTree) -> None:
    antecedentindex = gav(antecedent, "index")
    rhdindex = gav(rhdnode, "index")
    if antecedentindex != "":
        for node in stree.iter():
            nodeindex = gav(node, "index")
            if nodeindex == rhdindex:
                node.attrib["index"] = antecedentindex


def mkpp(
    rel: str,
    vz: str,
    obj1node: SynTree,
    begin,
    end,
    index,
    az=None,
) -> SynTree:
    ppnode = ET.Element("node", attrib={"cat": "pp", "rel": rel, "index": index})
    prepnode = ET.Element(
        "node",
        attrib={
            "pt": "vz",
            "lemma": vz,
            "word": vz,
            "rel": "hd",
            "begin": begin,
            "end": end,
            "vztype": "init",
        },
    )
    aznode = (
        ET.Element("node", attrib={"pt": "vz", "lemma": az, "word": az, "rel": "hdf"})
        if az is not None
        else None
    )
    newobj1node = copy.deepcopy(obj1node)
    newobj1node.attrib["rel"] = "obj1"
    ppnode.append(prepnode)
    ppnode.append(newobj1node)
    if aznode is not None:
        ppnode.append(aznode)
    return ppnode


def adaptvzlemma_inv(inlemma: str) -> str:
    if inlemma == "mee":
        result = "met"
    elif inlemma == "toe":
        result = "tot"
    else:
        result = inlemma
    return result


def relpronsubst(stree: SynTree) -> SynTree:
    newstree = copy.deepcopy(stree)
    npwithrelnodeids: List[int] = list(
        int(n)
        for n in xpath_values(
            stree, './/node[@cat="np" and node[@rel="mod" and @cat="rel"]]/@id'
        )
    )
    for npwithrelnodeid in npwithrelnodeids:
        npnode = find1(newstree, f'.//node[@id="{npwithrelnodeid}"]')
        if npnode is not None:
            relnodeid = find1(npnode, './node[@rel="mod" and @cat="rel"]/@id')
            rhdnode = find1(
                npnode, './node[@rel="mod" and @cat="rel"]/node[@rel="rhd"]'
            )
            rhdpt = gav(rhdnode, "pt")
            rhdframe = gav(rhdnode, "frame")
            antecedent = copy.deepcopy(npnode)
            relinantecedent = find1(antecedent, f'./node[@id="{relnodeid}"]')
            antecedent.remove(relinantecedent)
            antecedent.append(dummymod)
            antecedent.attrib["rel"] = "rhd"
            # adaptindexes(newstree, antecedent, rhdnode)  # the antecedent may have its own index yes,
            # but DO NOT do this, or you will have multiple incompatible antecedents
            relnode = find1(npnode, f'./node[@id="{relnodeid}"]')

            if rhdpt == "vnw":
                rhdindex = gav(rhdnode, "index")
                antecedent.attrib["index"] = rhdindex
                relnode.remove(rhdnode)
                relnode.insert(0, antecedent)
                # adapt the governing adposition if there is one
                govprep = find1(
                    newstree,
                    f'.//node[@pt="vz" and @rel="hd" and ../node[@index="{rhdindex}"]]',
                )
                if govprep is not None:
                    govprep.attrib["vztype"] = "init"
                    govprep.attrib["lemma"] = adaptvzlemma_inv(
                        cast(str, govprep.attrib["lemma"])
                    )
                # ET.dump(newstree)

            elif rhdframe.startswith("waar_adverb"):
                index = gav(rhdnode, "index")
                prep = rhdframe.split("(")[-1][:-1]
                if prep in vzazindex:
                    vz, az = vzazindex[prep]
                else:
                    vz = prep
                    az = None
                b, e = gav(rhdnode, "begin"), gav(rhdnode, "end")
                ppnode = mkpp("rhd", vz, antecedent, b, e, index, az=az)
                ppnode.attrib["rel"] = "rhd"
                relnode.remove(rhdnode)
                relnode.insert(0, ppnode)

    return newstree


def expandfull(rawstree: SynTree) -> SynTree:
    # possibly add getlcat
    stree = lowerpredm(rawstree)
    stree1 = relpronsubst(stree)
    stree2 = expandnonheadwords(stree1)
    stree3 = indextransform(stree2)
    return stree3


def isparticleverb(stree: SynTree) -> bool:
    lemma = gav(stree, "lemma")
    pt = gav(stree, "pt")
    result = (
        pt == "ww" and compoundsep in lemma
    )  # @@TODO we still must exclude other prefixesd such as on here
    return result


def mkparticlenode(wwnode: SynTree) -> Optional[SynTree]:
    lemma = gav(wwnode, "lemma")
    lemmaparts = lemma.split(compoundsep)
    if len(lemmaparts) >= 2:
        prtstr = lemmaparts[0]
        result = ET.Element(
            "node", attrib={"rel": "svp", "lemma": prtstr, "word": prtstr}
        )
    else:
        result = None
    return result


def expandsvplist(sons: List[SynTree]) -> List[List[SynTree]]:
    results = []
    prt = None
    if sons == []:
        results = [[]]
    else:
        head = sons[0]
        if isparticleverb(head):
            prt = mkparticlenode(head)
        tail = sons[1:]
        headresults = expandsvp(head)
        tail1results = expandsvplist(tail)
        if prt is not None:
            tail2results = [
                [copy.deepcopy(prt)] + tail1result for tail1result in tail1results
            ]
        else:
            tail2results = []
        tailresults = tail1results + tail2results
        for headresult in headresults:
            for tailresult in tailresults:
                headresultcopy = copy.deepcopy(headresult)
                tailresultcopy = copy.deepcopy(tailresult)
                newresult = [headresultcopy] + tailresultcopy
                results.append(newresult)
    return results


def copynode(stree: SynTree) -> SynTree:
    result = copy.copy(stree)
    # remove the children
    children = [child for child in result]
    for child in children:
        result.remove(child)
    return result


def expandsvp(stree: SynTree) -> List[SynTree]:
    results = []
    children = [child for child in stree]
    newsonslist = expandsvplist(children)
    for newsons in newsonslist:
        newnode = copynode(stree)
        newnode.extend(newsons)
        results.append(newnode)
    return results


def expandsvps(syntrees: List[SynTree]) -> List[SynTree]:
    results = []
    for syntree in syntrees:
        prtsyntrees = expandsvp(syntree)
        results.extend(prtsyntrees)
    return results


def gettopnode(stree):
    for child in stree:
        if child.tag == "node":
            return child
    return None


def ispronadv(node: SynTree) -> bool:
    lemma = gav(node, "lemma")
    result = lemma in pronadvlemmas
    if not result:
        lemmaoptions = lemma.split("|")
        result = any([lemmaoption in pronadvlemmas for lemmaoption in lemmaoptions])
    return result


def iscontentwordnode(node: SynTree) -> bool:
    nodept = gav(node, "pt")
    result = nodept in contentwordpts and not ispronadv(node)
    return result


def removeemptyalts(stree: SynTree) -> SynTree:
    newstree = copy.deepcopy(stree)
    for node in newstree.iter():
        if node.tag in {alternativetag, alternativestag} and len(node) == 0:
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
    return newstree


def mknearmissstructs(mwetrees: List[SynTree]) -> List[SynTree]:
    reducedmwetrees = []
    for mwetree in mwetrees:
        reducedmwetree = copy.deepcopy(mwetree)
        nodelist = list(
            reducedmwetree.iter()
        )  # turn it into a list to make sure it has been computed
        contentwordnodes = [node for node in nodelist if iscontentwordnode(node)]
        contentwordcount = len(contentwordnodes)
        for node in nodelist:
            if (
                "pt" in node.attrib
                and not iscontentwordnode(node)
                and contentwordcount > 1
            ):
                parent = node.getparent()
                if isinstance(parent, SynTree):
                    parent.remove(node)
                    grandparent = parent.getparent()
                    if isinstance(grandparent, SynTree) and len(parent) == 0:
                        grandparent.remove(parent)
            else:
                relevantproperties = coreproperties + subcatproperties + xpathproperties
                for att in node.attrib:
                    if att not in relevantproperties:
                        del node.attrib[att]
        cleanreducedmwetree = removeemptyalts(reducedmwetree)
        reducedmwetrees.append(cleanreducedmwetree)
    return reducedmwetrees


def mknearmiss(mwetrees: List[SynTree]) -> Xpathexpression:
    reducedmwetrees = mknearmissstructs(mwetrees)
    result = trees2xpath(reducedmwetrees)
    return result


def getlemmanodes(mwetree: SynTree) -> List[SynTree]:
    wordnodes = [
        node
        for node in mwetree.iter()
        if "pt" in node.attrib and "lemma" in node.attrib
    ]
    return wordnodes


def getmajorlemmas(mwetree: SynTree) -> List[SynTree]:
    wordnodes = getlemmanodes(mwetree)
    contentwordnodes = [node for node in mwetree.iter() if iscontentwordnode(node)]
    results = contentwordnodes if len(contentwordnodes) > 1 else wordnodes
    return results


def reorderchildren(children):
    nodechildren = []
    otherchildren = []
    for child in children:
        if child.tag == "node":
            nodechildren.append(child)
        else:
            otherchildren.append(child)
    result = nodechildren + otherchildren
    return result


def mksuperquery(mwetrees, mwe: str, rwq=False) -> Optional[Xpathexpression]:
    core = coremksuperquery(mwetrees, mwe, rwq)
    if core is not None:
        result = "//" + core
    else:
        result = None
    return result


def coremksuperquery(mwetrees, mwe: str, rwq=False) -> Optional[Xpathexpression]:
    """
    Generates the Major Lemma Query (mlq, earlier called the superquery).
    This uses the content words. If only one content word is in the expression, all the words are used.
    This way extensions for alternatives (such as the lemma "mijzelf|jezelf|zichzelf") are included.

    With rwq set to True it generates the Related Word Query (rwq), which finds a superset of the MLQ
    """
    debugmlq = False
    if debugmlq:
        print("canonicalform: mksuperquery: debugmlq: mwetrees")
        for mwetree in mwetrees:
            ET.dump(mwetree)
    if len(mwetrees) < 1:
        raise RuntimeError("Cannot generate superset query for empty tree set")

    mwetree = mwetrees[0]  # we only have to look at the first tree
    search_for = getmajorlemmas(mwetree)
    alllemmanodes = getlemmanodes(mwetree)

    target_node = ET.Element("node", attrib={"cat": "top"})
    children = []
    for node in search_for:
        cwlemma = gav(node, "lemma")
        cwpt = gav(node, "pt")

        # here we must do special things for prepositions (met/tot -> mee/toe; erP daarP etc) DONE
        # reflexives me je zich ons jullie and with zelf attached gaan al goed
        n = ET.Element("node", attrib=dict(lemma=cwlemma, pt=cwpt, axis="descendant"))
        if cwpt == "vz" and cwlemma in Radpositions:
            newlemma = adaptvzlemma(cwlemma)
            nmeetoe = ET.Element(
                "node", attrib=dict(lemma=newlemma, pt=cwpt, axis="descendant")
            )
            advpronnode = getpronadv(cwlemma, None)
            advpronnode.attrib["axis"] = "descendant"
            if cwlemma in ["mee", "toe"]:
                ns = mkalternativesnode([[n], [nmeetoe], [advpronnode]])
            else:
                ns = mkalternativesnode([[n], [advpronnode]])
        else:
            ns = n
        children.append(ns)
    # put the alternatives at the end; we must still do something if the alternatives and up as first
    children = reorderchildren(children)
    if debugmlq:
        print("canonicalform: mksuperquery: debugmlq")
        childcounter = 0
        for child in children:
            print(f"{childcounter}:")
            ET.dump(child)
            childcounter += 1

    if rwq:
        newchildren = []
        for child in children:
            newchild = getrwqnode(child, search_for, alllemmanodes)
            newchildren.append(newchild)
        children = newchildren

    if len(children) > 1:  # adapted by JO to avoid a crash and illegal Xpath output
        if "axis" in children[0].attrib:
            del children[0].attrib["axis"]
        for child in children[1:]:
            target_node.append(child)

        if children[0].tag == alternativestag:
            result = coredealwithalternatives(children[0], target_node)
        else:
            result = "{}/ancestor::alpino_ds/{}".format(
                tree2xpath(children[0]), tree2xpath(target_node)
            )
    else:
        result = None
        if len(search_for) == 1:
            print(f"Canonicalform: Warning: single word MWE: {mwe} ")

    return result


def oldcoremksuperquery(mwetrees, mwe: str) -> Optional[Xpathexpression]:
    """
    Generates the super query.
    This uses the content words. If only one content word is in the expression, all the words are used.
    This way extensions for alternatives (such as the lemma "mijzelf|jezelf|zichzelf") are included.
    """
    debugmlq = False
    if debugmlq:
        print("canonicalform: mksuperquery: debugmlq: mwetrees")
        for mwetree in mwetrees:
            ET.dump(mwetree)
    if len(mwetrees) < 1:
        raise RuntimeError("Cannot generate superset query for empty tree set")

    mwetree = mwetrees[0]  # we only have to look at the first tree
    search_for = getmajorlemmas(mwetree)

    target_node = ET.Element("node", attrib={"cat": "top"})
    children = []
    for node in search_for:
        cwlemma = gav(node, "lemma")
        cwpt = gav(node, "pt")

        # here we must do special things for prepositions (met/tot -> mee/toe; erP daarP etc) DONE
        # reflexives me je zich ons jullie and with zelf attached gaan al goed
        n = ET.Element("node", attrib=dict(lemma=cwlemma, pt=cwpt, axis="descendant"))
        if cwpt == "vz" and cwlemma in Radpositions:
            newlemma = adaptvzlemma(cwlemma)
            nmeetoe = ET.Element(
                "node", attrib=dict(lemma=newlemma, pt=cwpt, axis="descendant")
            )
            advpronnode = getpronadv(cwlemma, None)
            advpronnode.attrib["axis"] = "descendant"
            if cwlemma in ["mee", "toe"]:
                ns = mkalternativesnode([[n], [nmeetoe], [advpronnode]])
            else:
                ns = mkalternativesnode([[n], [advpronnode]])
        else:
            ns = n
        children.append(ns)
    # put the alternatives at the end; we must still do something if the alternatives and up as first
    children = reorderchildren(children)
    if debugmlq:
        print("canonicalform: mksuperquery: debugmlq")
        childcounter = 0
        for child in children:
            print(f"{childcounter}:")
            ET.dump(child)
            childcounter += 1

    if len(children) > 1:  # adapted by JO to avoid a crash and illegal Xpath output
        if "axis" in children[0].attrib:
            del children[0].attrib["axis"]
        for child in children[1:]:
            target_node.append(child)

        if children[0].tag == alternativestag:
            result = coredealwithalternatives(children[0], target_node)
        else:
            result = "{}/ancestor::alpino_ds/{}".format(
                tree2xpath(children[0]), tree2xpath(target_node)
            )
    else:
        result = None
        if len(search_for) == 1:
            print(f"Canonicalform: Warning: single word MWE: {mwe} ")

    return result


def dealwithalternatives(first, second) -> Xpathexpression:
    core = coredealwithalternatives(first, second)
    result = "//" + core
    return result


def coredealwithalternatives(first, second) -> Xpathexpression:
    results = []

    if first.tag != alternativestag:
        results = [(first, second)]
    else:
        expandedfirsts = expandalternatives(first)
        for expandedfirst in expandedfirsts:
            results.append((expandedfirst, second))

    xpathresults = []
    for first, second in results:
        if "axis" in first.attrib:
            del first.attrib["axis"]
        xpathresult = "{}/ancestor::alpino_ds/{}".format(
            tree2xpath(first), tree2xpath(second)
        )
        xpathresults.append(xpathresult)
    fullxpath = corexpaths2xpath(xpathresults)
    return fullxpath


def removeannotations(mwe: str) -> str:
    annotatedlist = preprocess_MWE(mwe)
    # annotations = [el[1] for el in annotatedlist]
    cleanmwe = space.join([el[0] for el in annotatedlist])
    return cleanmwe


def addalternativelemmas(syntree: SynTree) -> SynTree:
    showtrees = False
    if showtrees:
        showtree(syntree, "canonicalform:addalternativelemmas: syntree")
    newsyntree = copy.deepcopy(syntree)
    for node in newsyntree.iter():
        if "lemma" in node.attrib:
            thelemma = node.attrib["lemma"]
            if thelemma in reversemwuwordlemmadict:
                altlemmas = reversemwuwordlemmadict[thelemma]
                altlemmas = [thelemma] + altlemmas
                node.attrib["lemma"] = f'{"|".join(altlemmas)}'
    result = newsyntree
    if showtrees:
        showtree(newsyntree, "canonicalform:addalternativelemmas: newsyntree")
    return result


def mapaddalternativelemmas(syntrees: List[SynTree]) -> List[SynTree]:
    results = []
    for syntree in syntrees:
        newsyntree = addalternativelemmas(syntree)
        results.append(newsyntree)
    return results


def generatemwestructures(mwe: str, lcatexpansion=True, mwetree=None) -> List[SynTree]:
    annotatedlist = preprocess_MWE(mwe)
    annotations = [el[1] for el in annotatedlist]
    cleanmwe = space.join([el[0] for el in annotatedlist])

    # parse the utterance
    if mwetree is None:
        unexpandedfullmweparse = parse(cleanmwe)
    else:
        unexpandedfullmweparse = mwetree

    if lcatexpansion:
        fullmweparse = expandnonheadwords(unexpandedfullmweparse)
    else:
        fullmweparse = unexpandedfullmweparse
    # ET.dump(fullmweparse)
    mweparse = gettopnode(fullmweparse)
    nodeidwordmap = mknodeidwordmap(mweparse)
    newtreesb = transformtree(mweparse, annotations)
    newtreesa = mapaddalternativelemmas(newtreesb)
    newtrees = []
    for newtreea in newtreesa:
        if isinstance(newtreea, SynTree):
            newtrees += newgenvariants(newtreea, nodeidwordmap)
    cleantrees = [removesuperfluousindexes(newtree) for newtree in newtrees]

    prtcleantrees = cleantrees  # expandsvps(cleantrees) # this moved to newgenvariants
    return prtcleantrees


def mknodeidwordmap(stree: SynTree) -> Dict[int, str]:
    resultdict = {}
    wordnodes = stree.xpath(".//node[@word]")
    for wordnode in wordnodes:
        if "id" in wordnode.attrib and "word" in wordnode.attrib:
            theid = wordnode.attrib["id"]
            theword = wordnode.attrib["word"]
            resultdict[theid] = theword
        else:
            # should not occur
            print(f"No id or word in node {str(wordnode)}", file=sys.stderr)
    return resultdict


def mkmwestructs(newtreesa, nodeidwordmap):
    newtrees = []
    for newtreea in newtreesa:
        newtrees += newgenvariants(newtreea, nodeidwordmap)
    cleantrees = [removesuperfluousindexes(newtree) for newtree in newtrees]
    return cleantrees


def generatequeries(mwe: str, lcatexpansion=True, mwetree=None) -> Tuple[
    Xpathexpression,
    Xpathexpression,
    Optional[Xpathexpression],
    Optional[Xpathexpression],
]:
    """
    Generates three MWE queries

    Args:
        mwe (str): (annotated) canonical form of a multi word expression
        lcatexpansion (bool, optional): whether single word non heads should be placed below a phrasal node. Defaults to True.

    Returns:
        Tuple[Xpathexpression, Xpathexpression, Xpathexpression]: mwequery, nearmissquery, supersetquery
    """

    annotatedlist = preprocess_MWE(mwe)
    annotations = [el[1] for el in annotatedlist]
    cleanmwe = space.join([el[0] for el in annotatedlist])

    # parse the utterance
    if mwetree is None:
        unexpandedfullmweparse = parse(cleanmwe)
    else:
        unexpandedfullmweparse = mwetree

    if lcatexpansion:
        fullmweparse = expandnonheadwords(unexpandedfullmweparse)
    else:
        fullmweparse = unexpandedfullmweparse
    # ET.dump(fullmweparse)
    mweparse = gettopnode(fullmweparse)
    nodeidwordmap = mknodeidwordmap(mweparse)
    # transform the tree to a form from which queries can be derived
    newtreesb = transformtree(mweparse, annotations)
    newtreesa = mapaddalternativelemmas(newtreesb)
    newtrees: List[SynTree] = []
    # alternative trees
    for newtreea in newtreesa:
        if isinstance(newtreea, SynTree):
            newtrees += newgenvariants(newtreea, nodeidwordmap)
    cleantrees = [removesuperfluousindexes(newtree) for newtree in newtrees]
    mwequery = trees2xpath(cleantrees, expanded=True)

    # nearmissquery
    nearmissquery = mknearmiss(cleantrees)

    # major lemma query
    supersetquery = mksuperquery(newtreesa, mwe)

    # related word query
    relatedwordquery = mksuperquery(newtrees, mwe, rwq=True)

    return mwequery, nearmissquery, supersetquery, relatedwordquery


def selfapplyqueries(utt, mwequery, nearmissquery, supersetquery, lcatexpansion=True):
    unexpandedfullparse = parse(utt)
    unexpandedfullparse = lowerpredm(unexpandedfullparse)
    # ET.dump(unexpandedfullparse)

    # in the real application this should be done on the treebank's index
    supersetnodes = unexpandedfullparse.xpath(supersetquery)

    nearmissnodes = []
    mwenodes = []
    for supersetnode in supersetnodes:
        if lcatexpansion:
            fullparse = expandnonheadwords(supersetnode)
        else:
            fullparse = supersetnode
        # ET.dump(fullparse)

        indexpfullparse = indextransform(fullparse)

        # ET.dump(indexpfullparse)
        nearmissnodes += indexpfullparse.xpath(nearmissquery)
        mwenodes += indexpfullparse.xpath(mwequery)

    return (mwenodes, nearmissnodes, supersetnodes)


def markutt(utt: str, nodes: List[SynTree]) -> str:
    tokens = utt.split()
    if nodes == []:
        result = utt
    else:
        node = nodes[0]
        nodeyield = getnodeyield(node)
        markbegins = [int(gav(node, "begin")) for node in nodeyield]
        markedutttokens = [
            mark(token) if i in markbegins else token for i, token in enumerate(tokens)
        ]
        result = space.join(markedutttokens)
    return result


def mark(wrd: str) -> str:
    return f"*{wrd}*"


def xpath(tree: SynTree, query: Xpathexpression) -> Iterable[SynTree]:
    result = tree.xpath(query)
    if not result:
        return []
    elif not isinstance(result, list):
        raise ValueError(f"Unexpected type: {type(result)}")
    else:
        for item in result:
            if not isinstance(item, SynTree):
                raise ValueError(f"Unexpected type: {type(item)}")
            yield item


def xpath_values(tree: SynTree, query: Xpathexpression) -> Iterable[str]:
    result = tree.xpath(query)
    if not result:
        return []
    elif not isinstance(result, list):
        return [str(result)]
    else:
        for value in result:
            yield str(value)


def applyqueries(
    treebank: Dict[str, SynTree],
    mwe: str,
    mwequery: Xpathexpression,
    nearmissquery: Xpathexpression,
    supersetquery: Xpathexpression,
    fullexpansion=True,
    verbose=True,
) -> Dict[str, List[Tuple[List[SynTree], List[SynTree], List[SynTree]]]]:
    """
    Applies three queries on a treebank and returns a dictionary with their hits.
    Args:
        treebank (Dict[str, SynTree]): syntactical trees with the ID of each tree used as key
        mwe (str): only needed for print
        mwequery (Xpathexpression): query for finding an MWE
        nearmissquery (Xpathexpression): query for finding near misses of that MWE
        supersetquery (Xpathexpression): super set query
        fullexpansion (bool, optional): this should have the same value as used when generating queries. Defaults to True.

    Returns:
        Dict[str, Tuple[List[SynTree], List[SynTree], List[SynTree]]]: tree id and the hits for each query
    """
    allresults: Dict[str, List[Tuple[List[SynTree], List[SynTree], List[SynTree]]]] = {}
    for treeid, tree in treebank.items():
        allresults[treeid] = []
        unexpandedfullparse = lowerpredm(tree)
        # ET.dump(unexpandedfullparse)

        # in the real application this should be done on the treebank's index
        supersetnodes: List[SynTree] = list(xpath(unexpandedfullparse, supersetquery))

        nearmissnodes: List[SynTree] = []
        mwenodes: List[SynTree] = []
        for supersetnode in supersetnodes:
            if fullexpansion:
                expandedparse = expandfull(supersetnode)
            else:
                expandedparse = supersetnode
            # ET.dump(expandedparse)
            # fullurl = previewurl(expandedparse)

            # ET.dump(indexpfullparse)
            nearmissnodes += xpath(expandedparse, nearmissquery)
            mwenodes += xpath(expandedparse, mwequery)

            allresults[treeid].append((mwenodes, nearmissnodes, supersetnodes))
            if verbose:
                if mwenodes != []:
                    allresults[treeid].append((mwenodes, nearmissnodes, supersetnodes))
                    if treeid != mwe:
                        print(f"<{treeid}>  found by query for <{mwe}>")
                        print(markutt(treeid, mwenodes))
                        print(markutt(treeid, nearmissnodes))
                        print(markutt(treeid, supersetnodes))
                else:
                    if treeid == mwe:
                        print(f"    <{treeid}> not found by query for <{mwe}>")
                        print(
                            f"    mwenodes:{len(mwenodes)}; nearmiss:{len(nearmissnodes)}; superset:{len(supersetnodes)}"
                        )

    return allresults
