"""
Module to identify MWEs on the basis of information in the Alpino treebank and partially from the Alpino lexicon
Based on a similar module operating on UD structures cretaed by Gosse Bouma
But we do not include here the examples derived from the Alpino lexicon, we rely on DUCAME for that
See https://github.com/gossebouma/Parseme-NL/blob/main/Parseme-NL.ipynb
"""

from .mwemeta import MWEMeta
from .mwetypes import getmwetype
from sastadev.treebankfunctions import (
    getattval as gav,
    getnodeyield,
    getsentence,
    terminal,
)
from sastadev.sastatypes import SynTree
from typing import List, Optional, Tuple
import sys

space = " "
plussym = "+"
underscore = "_"
compoundsym = underscore

# we turn these into entries in DUCAME if they are not present there yet
# dictionary derived from alpino with fixed expressions (fixed) and semi-flexible fixed expressions that are mapped to regular deprels in UD
# with open('alpino_dictionary.json') as f:
#     dictionary = json.load(f)


# zie ook https://parsemefr.lis-lab.fr/parseme-st-guidelines/1.3/?page=irv#irv-overlap-vid
# schreef op zijn naam, also incude op zijn? (deps of naam, cmp:prt?) no

# alternative: for a given verb: find all mwe-lexical deps, collect classes, collect ids,
# (for one-word-particle cases: add VPC if not already in classes)
# then decide on label on basis of class(es)

# grep VERB nl_lassysmall-ud-all.cupt |cut -f 8 |sortnr


def isterminal(node: SynTree) -> bool:
    result = "word" in node.attrib
    return result


def getheadof(node: SynTree) -> Optional[SynTree]:
    firstcnj = None
    for child in node:
        if gav(child, "rel") == "hd":
            return child
        if gav(child, "rel") == "cnj":
            if firstcnj is None:
                firstcnj = child
            else:
                if int(gav(child, "begin")) < int(gav(firstcnj, "begin")):
                    firstcnj = child
    if firstcnj is not None:
        if isterminal(firstcnj):
            return firstcnj
        else:
            result = getheadof(firstcnj)
            return result
    else:
        return None


def isparticleverb(node: SynTree) -> bool:
    lemma = gav(node, "lemma")
    pt = gav(node, "pt")
    lemmaparts = lemma.split(compoundsym)
    result = pt == "ww" and len(lemmaparts) == 2 and lemmaparts[0] != "on"
    return result


def reducepronadv(wrd: str) -> str:
    if wrd[0:4] in {"hier", "daar", "waar"}:
        rawresult = wrd[4:]
    elif wrd[0:2] in {"er"}:
        rawresult = wrd[2:]
    else:
        return wrd
    if rawresult == "mee":
        result = "met"
    elif rawresult == "toe":
        result = "tot"
    else:
        result = rawresult
    return result


def getleavespositions(syntree: SynTree) -> List[str]:
    leaves = getnodeyield(syntree)
    leavespositions = [gav(leaf, "end") for leaf in leaves]
    return leavespositions


def getmweid(zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode) -> str:
    if zichnode is None:
        zichstr = ""
    else:
        zichstr = "zich"
    if wwsvpnode is None:
        wwsvpstr = ""
    else:
        wwsvpstr = gav(wwsvpnode, "lemma")
    if iavnode is None:
        iavstr = ""
    else:
        iavstr = gav(iavnode, "lemma")
        iavstr = reducepronadv(iavstr)
    svpstrs = [gav(node, "lemma") for node in svpnodes]
    verbstr = gav(verb, "lemma")
    rawresultlist = [zichstr] + svpstrs + [verbstr, wwsvpstr, iavstr]
    resultlist = [wrd for wrd in rawresultlist if wrd != ""]
    result = plussym.join(resultlist)
    return result


def getprtfromlemma(prtwwnode: SynTree) -> str:
    prtwwnodelemma = gav(prtwwnode, "lemma")
    lemmaparts = prtwwnodelemma.split(compoundsym)
    result = lemmaparts[0] if len(lemmaparts) > 1 else ""
    return result


def getsvpnodes(nodes: List[SynTree]) -> List[SynTree]:
    prtwwnode = None
    prtnode = None
    wwprt = None
    excludednodes = []
    for node in nodes:
        if gav(node, "rel") == "svp" and "pt" in node.attrib:
            prtnode = node
            prtnodelemma = gav(prtnode, "lemma")
        if gav(node, "pt") == "ww" and compoundsym in gav(node, "lemma"):
            prtwwnode = node
    if prtwwnode is not None:
        wwprt = getprtfromlemma(prtwwnode)
    if prtnode is not None and wwprt is not None and prtnodelemma == wwprt:
        excludednodes.append(prtnode)
    results = [node for node in nodes if node not in excludednodes]
    return results


def oldgetmweid(mwenodes: List[SynTree]) -> str:
    if mwenodes == []:
        return ""
    nonheads = [gav(node, "word") for node in mwenodes[:-1]]
    head = gav(mwenodes[-1], "lemma")
    result = plussym.join(nonheads + [head])
    return result


def getintpositions(mwenodes: List[SynTree]) -> List[int]:
    intpositions = []
    nodestrlist = []
    for mwenode in mwenodes:
        nodestr = gav(mwenode, "lemma") if mwenode is not None else "None"
        nodestrlist.append(nodestr)
    nodeliststr = space.join(nodestrlist)

    for mwenode in mwenodes:
        if mwenode is None:
            print(f"None node encountered in {nodeliststr} ", file=sys.stderr)
        else:
            position = gav(mwenode, "end")
            intposition = int(position)
            intpositions.append(intposition)

    sortedintpositions = sorted(intpositions)
    return sortedintpositions


def getalpinomwes(syntree: SynTree, sentenceid=None) -> List[MWEMeta]:  # noqa: C901
    mwemetas = []
    mwelexicon = "Alpino"
    sentence = getsentence(syntree)
    mwequerytype = "MEQ"
    iavnode = None
    zichnode = None
    partnode = None
    verbs = syntree.xpath('.//node[@pt="ww" ]')
    for verb in verbs:
        iavnode = None
        zichnode = None
        partnode = None
        classes = []
        mwenodes = []
        svpnodes = []
        wwsvpnode = None
        siblings = verb.xpath("../node")
        for sibling in siblings:
            if sibling == verb:
                continue
            siblingrel = gav(sibling, "rel")
            if siblingrel == "pc":
                classes += ["IAV"]
                if terminal(sibling):
                    mwenodes.append(sibling)
                    iavnode = sibling
                else:
                    siblinghead = getheadof(sibling)
                    mwenodes.append(siblinghead)
                    iavnode = siblinghead
            if siblingrel == "se":
                if terminal(sibling):
                    zichnode = sibling
                else:
                    zichnode = getheadof(sibling)
                mwenodes.append(zichnode)
                classes.append("IRV")
            if siblingrel == "svp":
                if isparticleverb(verb):
                    if terminal(sibling):
                        siblingpt = gav(sibling, "pt")
                        if siblingpt == "ww":
                            classes += ["MVC"]
                            wwsvpnode = sibling
                            mwenodes.append(sibling)
                        else:
                            wwprt = getprtfromlemma(verb)
                            siblinglemma = gav(sibling, "lemma")
                            if wwprt == siblinglemma:
                                classes += ["VPC.full"]
                                # partnode = sibling
                                mwenodes.append(sibling)
                            else:
                                pass  # we ignore other svp nodes and rely for this on DUCAME
                    else:
                        if len(sibling) == 1:
                            siblinghead = sibling[0]
                            siblingpt = gav(siblinghead, "pt")
                            siblinglemma = gav(siblinghead, "lemma")
                            wwprt = getprtfromlemma(verb)
                            if siblingpt == "ww":
                                classes += ["MVC"]
                            elif wwprt == siblinglemma:
                                classes += ["VPC.full"]
                                # partnode = sibling
                                mwenodes.append(sibling)
                            else:
                                classes += ["VID"]
                        else:
                            siblingcat = gav(sibling, "cat")
                            siblingleaves = getnodeyield(sibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            if siblingcat in ["ti", "inf"]:
                                classes.append("MVC")
                                mwenodes += siblingleaves
                            else:
                                pass  # we ignore these and rely on DUCAME
                else:
                    if terminal(sibling):
                        siblingpt = gav(sibling, "pt")
                        mwenodes.append(sibling)
                        if siblingpt == "ww":
                            if isparticleverb(sibling):
                                classes = ["VID", "VPC.full"]
                            else:
                                classes += ["MVC"]
                            wwsvpnode = sibling
                    else:
                        (mwuppok, mwupphd, mwuppleaves) = ismwupp(sibling)
                        if mwuppok:
                            mwenodes += mwuppleaves
                            svpnodes = mwuppleaves
                            classes += ["VID"]
                        else:
                            siblingcat = gav(sibling, "cat")
                            siblingleaves = getnodeyield(sibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            wwsvpnodecands = [
                                svpnode
                                for svpnode in svpnodes
                                if gav(svpnode, "pt") == "ww"
                            ]
                            if wwsvpnodecands != []:
                                wwsvpnode = wwsvpnodecands[0]
                                svpnodes = [
                                    svpnode
                                    for svpnode in svpnodes
                                    if svpnode != wwsvpnode
                                ]
                            else:
                                wwsvpnode = None
                            mwenodes += siblingleaves
                            if siblingcat in ["ti", "inf"]:
                                classes.append("MVC")
                            else:
                                classes += ["VID"]
        if "VPC.full" not in classes and isparticleverb(verb):
            classes.append("VPC.full")
        if classes != []:
            mwenodes.append(verb)
            intpositions = getintpositions(mwenodes)
            headposition = int(gav(verb, "end"))
            headpos = "ww"
            parsemetype = getmwetype(verb, headpos, classes)
            if sentenceid is None:
                sentenceid = ""
            mweid = getmweid(zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
            mwemeta = MWEMeta(
                sentence,
                sentenceid,
                mweid,
                mwelexicon,
                mwequerytype,
                mweid,
                intpositions,
                headposition,
                headpos,
                classes,
                parsemetype,
            )
            mwemetas.append(mwemeta)
    vzs = syntree.xpath(
        './/node[@pt="vz" and @rel="hd" ]'
    )  # no condition on vztype because of 'ergens op af'
    for vz in vzs:
        vzposition = int(gav(vz, "end"))
        vzazsiblings = vz.xpath('../node[@pt="vz" and @vztype="fin" and @rel="hdf"]')
        for az in vzazsiblings:
            vzlemma = gav(vz, "lemma")
            azlemma = gav(az, "lemma")
            mweid = f"{vzlemma}...{azlemma}"
            azposition = int(gav(az, "end"))
            intpositions = sorted([vzposition, azposition])
            headposition = vzposition
            headpos = gav(vz, "pt")
            classes = ["PID"]
            parsemetype = getmwetype(vz, headpos, classes)
            mwemeta = MWEMeta(
                sentence,
                sentenceid,
                mweid,
                mwelexicon,
                mwequerytype,
                mweid,
                intpositions,
                headposition,
                headpos,
                classes,
                parsemetype,
            )
            mwemetas.append(mwemeta)
    return mwemetas


def ismwupp(node: SynTree) -> Tuple[bool, SynTree, List[SynTree]]:
    mwunode = None
    mwunodehdnode = None
    pcnode = None
    pcnodehdnode = None
    nodecat = gav(node, "cat")
    if nodecat == "pp":
        for child in node:
            if gav(child, "cat") == "mwu":
                mwunode = child
            if gav(child, "cat") == "pp" and gav(child, "rel") == "pc":
                pcnode = child
        if pcnode is not None:
            pcnodehdnode = getheadof(pcnode)
        if mwunode is not None:
            mwunodehdnode = mwunode[0]
        if (
            mwunode is not None
            and pcnode is not None
            and pcnodehdnode is not None
            and mwunodehdnode is not None
        ):
            mwuleaves = getnodeyield(mwunode) + [pcnodehdnode]
            result = (True, mwunodehdnode, mwuleaves)
            return result

    return (False, None, [])
