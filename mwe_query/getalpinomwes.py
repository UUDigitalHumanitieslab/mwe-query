"""
Module to identify MWEs on the basis of information in the Alpino treebank and partially from the Alpino lexicon
Based on a similar module operating on UD structures cretaed by Gosse Bouma
But we do not include here the examples derived from the Alpino lexicon, we rely on DUCAME for that
See https://github.com/gossebouma/Parseme-NL/blob/main/Parseme-NL.ipynb
"""
from lexicons import cranberryparticleslexicon, irvindeplexicon, notSCVslexicon, prenomadjdeelwoordenlexicon, vpcsemilexicon
from mwemeta import MWEMeta
from mwetypes import getmwetype, IAV, IRV, IRVd, IRVi, MVC, PID, VID, VPCfull, VPCVID, VPClight, VPCmaybelight, \
    vpcmap, vpcclass2type
from sastadev.treebankfunctions import (
    getattval as gav,
    getnodeyield,
    getsentence,
    terminal,
)
from sastadev.sastatypes import SynTree  # , Relation
from typing import List, Optional, Tuple
import sys
from copy import deepcopy


Relation = str
space = " "
plussym = "+"
underscore = "_"
compoundsym = underscore
maybe = 'maybe'

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


def additionalconditionsprtverb(node: SynTree) -> bool:
    lemma = gav(node, "lemma")
    pos = gav(node, "pos")
    result = lemma not in notSCVslexicon and pos != "adv"
    return result


def isparticleverb(node: SynTree) -> bool:
    lemma = gav(node, "lemma")
    pt = gav(node, "pt")
    # pos = gav(node, "pos")
    lemmaparts = lemma.split(compoundsym)
    result = pt == "ww" and len(
        lemmaparts) == 2 and lemmaparts[0] != "on" and additionalconditionsprtverb(node)
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
    result = ''.join(lemmaparts[:-1]) if len(lemmaparts) > 1 else ""
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
            print(
                f"getalpinomwes:getintpositions: None node encountered in {nodeliststr} ", file=sys.stderr)
        else:
            position = gav(mwenode, "end")
            intposition = int(position)
            intpositions.append(intposition)

    sortedintpositions = sorted(intpositions)
    return sortedintpositions


def getrealparentrel(node: SynTree) -> Relation:
    parent = node.getparent()
    noderel = gav(node, 'rel')
    parentrel = gav(parent, 'rel') if parent is not None else noderel
    if parentrel == 'cnj':
        grandparent = parent.getparent()
        grandparentrel = gav(grandparent, 'rel')
        result = grandparentrel
    else:
        result = parentrel
    return result


def truelyverbal(verb: SynTree) -> bool:
    verblemma = gav(verb, 'lemma')
    verbwvorm = gav(verb, 'wvorm')
    verbpositie = gav(verb, 'positie')
    isprenominaladjective = verbpositie == 'prenom' and \
        verblemma in prenomadjdeelwoordenlexicon and \
        prenomadjdeelwoordenlexicon[verblemma] == verbwvorm
    isnominalisedparticiple = verbpositie == 'nom' and verbwvorm in [
        'vd', 'od']
    realparentrel = getrealparentrel(verb)
    afgezien = verblemma in ['af_zien', 'om_keren'] and verbwvorm == 'vd' and \
        verbpositie == "vrij" and realparentrel != "vc"
    result = not isprenominaladjective and not isnominalisedparticiple and not afgezien
    return result


def getvpcclass(verb: SynTree) -> str:
    prt = getprtfromlemma(verb)
    if iscranberryprt(prt):
        result = VPCVID
    else:
        result = getsemi(verb)
    return result


def iscranberryprt(prt: str) -> bool:
    result = prt in cranberryparticleslexicon
    return result


def getsemi(node: SynTree) -> str:
    lemma = gav(node, 'lemma')
    if lemma in vpcsemilexicon:
        status = vpcsemilexicon[lemma]
        if status == maybe:
            result = VPCmaybelight
        else:
            result = VPClight
    else:
        result = VPCfull
    return result


def oldalpinomwes(syntree: SynTree, sentenceid=None) -> List[MWEMeta]:  # noqa: C901
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
        verblemma = gav(verb, 'lemma')
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
                                thevpc = VPClight if verblemma in vpcsemilexicon else VPCfull
                                classes += [vpcmap(thevpc, siblingpt)]
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
                                classes += [MVC]
                            elif wwprt == siblinglemma:
                                thevpc = VPClight if verblemma in vpcsemilexicon else VPCfull
                                classes += [vpcmap(thevpc, siblingpt)]
                                # partnode = sibling
                                mwenodes.append(sibling)
                            else:
                                classes += [VID]
                        else:
                            siblingcat = gav(sibling, "cat")
                            siblingleaves = getnodeyield(sibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            if siblingcat in ["ti", "inf"]:
                                classes.append(MVC)
                                mwenodes += siblingleaves
                            else:
                                pass  # we ignore these and rely on DUCAME
                else:
                    if terminal(sibling):
                        siblingpt = gav(sibling, "pt")
                        mwenodes.append(sibling)
                        if siblingpt == "ww":
                            if isparticleverb(sibling):
                                thevpc = VPClight if verblemma in vpcsemilexicon else VPCfull
                                classes = [VID, vpcmap(thevpc, siblingpt)]
                            else:
                                classes += [MVC]
                            wwsvpnode = sibling
                    else:
                        (mwuppok, mwupphd, mwuppleaves) = ismwupp(sibling)
                        if mwuppok:
                            mwenodes += mwuppleaves
                            svpnodes = mwuppleaves
                            classes += [VID]
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
                                classes.append(MVC)
                            else:
                                classes += [VID]
        if "VPC.full" not in classes and isparticleverb(verb):
            classes.append(VPCfull)
        if classes != []:
            mwenodes.append(verb)
            intpositions = getintpositions(mwenodes)
            headposition = int(gav(verb, "end"))
            headpos = "ww"
            headlemma = gav(verb, 'lemma')
            parsemetype = getmwetype(verb, headpos, classes)
            if sentenceid is None:
                sentenceid = ""
            mweid = getmweid(zichnode, svpnodes, partnode,
                             verb, wwsvpnode, iavnode)
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
                headlemma,
                deepcopy(classes),
                parsemetype,
            )
            mwemetas.append(mwemeta)
    vzs = syntree.xpath(
        './/node[@pt="vz" and @rel="hd" ]'
    )  # no condition on vztype because of 'ergens op af'
    for vz in vzs:
        vzposition = int(gav(vz, "end"))
        vzazsiblings = vz.xpath(
            '../node[@pt="vz" and @vztype="fin" and @rel="hdf"]')
        for az in vzazsiblings:
            vzlemma = gav(vz, "lemma")
            azlemma = gav(az, "lemma")
            mweid = f"{vzlemma}...{azlemma}"
            azposition = int(gav(az, "end"))
            intpositions = sorted([vzposition, azposition])
            headposition = vzposition
            headpos = gav(vz, "pt")
            headlemma = gav(vz, 'lemma')
            classes = [PID]
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
                headlemma,
                deepcopy(classes),
                parsemetype,
            )
            mwemetas.append(mwemeta)
    return mwemetas


def getalpinomwes(syntree: SynTree, sentenceid=None) -> List[MWEMeta]:  # noqa: C901
    mwemetas = []
    mwelexicon = "Alpino"
    sentence = getsentence(syntree)
    mwequerytype = "MEQ"
    iavnode = None
    zichnode = None
    partnode = None
    verbs = syntree.xpath('.//node[@pt="ww"]')
    for verb in verbs:
        if not truelyverbal(verb):
            continue
        verbrel = gav(verb, 'rel')
        headposition = int(gav(verb, "end"))
        headpos = "ww"
        headlemma = gav(verb, 'lemma')
        iavnode = None
        zichnode = None
        partnode = None
        classes = []
        mwenodes = []
        svpnodes = []
        wwsvpnode = None
        siblings = verb.xpath("../node")
        if isparticleverb(verb) and verbrel != "hd":
            mwenodes.append(verb)
            intpositions = getintpositions(mwenodes)
            # @@ get the svp and its pt
            mweid = getmweid(zichnode, svpnodes, partnode,
                             verb, wwsvpnode, iavnode)
            theclass = getvpcclass(verb)
            classes = [theclass]
            parsemetype = vpcclass2type(theclass)
            if parsemetype is not None:
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
                    headlemma,
                    deepcopy(classes),
                    parsemetype,
                )
                mwemetas.append(mwemeta)
        if verbrel == 'hd':
            if isparticleverb(verb):
                mwenodes.append(verb)
                svpsiblings = [sibling for sibling in siblings if gav(
                    sibling, "rel") == 'svp']
                if len(svpsiblings) == 1:
                    thesvpsibling = svpsiblings[0]
                    if terminal(thesvpsibling):
                        thesvpsiblingpt = gav(thesvpsibling, "pt")
                        if thesvpsiblingpt == "ww":
                            if verbrel == "hd":
                                mwenodes.append(thesvpsibling)
                                intpositions = getintpositions(mwenodes)
                                mweid = getmweid(
                                    zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
                                classes += [MVC]
                                parsemetype = MVC
                                if parsemetype is not None:
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
                                        headlemma,
                                        deepcopy(classes),
                                        parsemetype,
                                    )
                                    mwemetas.append(mwemeta)
                        else:  # svp sibling is not a verb
                            wwprt = getprtfromlemma(verb)
                            thesvpsiblinglemma = gav(thesvpsibling, "lemma")
                            thesvpsiblingpt = gav(thesvpsibling, "pt")
                            if wwprt == thesvpsiblinglemma:
                                theclass = getvpcclass(verb)
                                vpcclass = vpcmap(theclass, thesvpsiblingpt)
                                classes += [vpcclass]
                                mwenodes.append(thesvpsibling)
                                intpositions = getintpositions(mwenodes)
                                mweid = getmweid(
                                    zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
                                parsemetype = vpcclass2type(vpcclass)
                                if parsemetype is not None:
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
                                        headlemma,
                                        deepcopy(classes),
                                        parsemetype,
                                    )
                                    mwemetas.append(mwemeta)
                            else:
                                pass  # we ignore other svp nodes and rely for this on DUCAME
                    else:           # nonterminal svp sibling
                        if len(thesvpsibling) == 1:
                            siblinghead = thesvpsibling[0]
                            siblingpt = gav(siblinghead, "pt")
                            siblingheadlemma = gav(siblinghead, "lemma")
                            wwprt = getprtfromlemma(verb)
                            if siblingpt == "ww":
                                classes += [MVC]
                                parsemetype = MVC
                                mwenodes.append(siblinghead)
                                intpositions = getintpositions(mwenodes)
                                mweid = getmweid(
                                    zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
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
                                    headlemma,
                                    deepcopy(classes),
                                    parsemetype,
                                )
                                mwemetas.append(mwemeta)
                            elif wwprt == siblingheadlemma:
                                theclass = getvpcclass(verb)
                                vpcclass = vpcmap(theclass, siblingpt)
                                classes += [vpcclass]
                                parsemetype = vpcclass2type(vpcclass)
                                mwenodes.append(siblinghead)
                                intpositions = getintpositions(mwenodes)
                                mweid = getmweid(
                                    zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
                                if parsemetype is not None:
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
                                        headlemma,
                                        deepcopy(classes),
                                        parsemetype,
                                    )
                                    mwemetas.append(mwemeta)
                            else:   # siblinghead is not a prt or verb
                                classes += [VID]
                                parsemetype = VID
                                mwenodes.append(siblinghead)
                                intpositions = getintpositions(mwenodes)
                                mweid = getmweid(
                                    zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
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
                                    headlemma,
                                    deepcopy(classes),
                                    parsemetype,
                                )
                                mwemetas.append(mwemeta)
                        else:  # sibling has multiple children
                            siblingcat = gav(thesvpsibling, "cat")
                            siblingleaves = getnodeyield(thesvpsibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            if siblingcat in ["ti", "inf"]:
                                classes.append(MVC)
                                parsemetype = MVC
                                mwenodes += siblingleaves
                                intpositions = getintpositions(mwenodes)
                                mweid = getmweid(
                                    zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
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
                                    headlemma,
                                    deepcopy(classes),
                                    parsemetype,
                                )
                                mwemetas.append(mwemeta)

                            else:
                                pass  # we ignore these and rely on DUCAME
                elif len(svpsiblings) == 0:  # wil this still occur?
                    mwenodes.append(verb)
                    intpositions = getintpositions(mwenodes)
                    mweid = getmweid(zichnode, svpnodes,
                                     partnode, verb, wwsvpnode, iavnode)
                    theclass = getvpcclass(verb)
                    classes = [theclass]
                    parsemetype = vpcclass2type(theclass)
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
                        headlemma,
                        deepcopy(classes),
                        parsemetype,
                    )
                    mwemetas.append(mwemeta)

                else:
                    pass  # we leave these to DUCAME
            if not isparticleverb(verb) and additionalconditionsprtverb(verb):
                svpsiblings = [sibling for sibling in siblings if gav(
                    sibling, 'rel') == 'svp']
                if len(svpsiblings) == 1:
                    thesvpsibling = svpsiblings[0]
                    mwenodes.append(verb)
                    if terminal(thesvpsibling):
                        thesvpsiblingpt = gav(thesvpsibling, "pt")
                        mwenodes.append(thesvpsibling)
                        if thesvpsiblingpt == "ww":
                            classes += [MVC]
                            parsemetype = MVC
                        else:
                            classes += [VID]
                            parsemetype = VID
                        wwsvpnode = thesvpsibling
                        intpositions = getintpositions(mwenodes)
                        mweid = getmweid(zichnode, svpnodes,
                                         partnode, verb, wwsvpnode, iavnode)
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
                            headlemma,
                            deepcopy(classes),
                            parsemetype,
                        )
                        mwemetas.append(mwemeta)
                    else:
                        (mwuppok, mwupphd, mwuppleaves) = ismwupp(thesvpsibling)
                        if mwuppok:
                            mwenodes += mwuppleaves
                            svpnodes = mwuppleaves
                            classes += [VID]
                            parsemetype = VID
                        else:
                            siblingcat = gav(thesvpsibling, "cat")
                            siblingleaves = getnodeyield(thesvpsibling)
                            svpnodes = getsvpnodes(siblingleaves)
                            wwsvpnodecands = [
                                svpnode for svpnode in svpnodes if gav(svpnode, "pt") == "ww"]
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
                                classes.append(MVC)
                                parsemetype = MVC
                            else:
                                classes += [VID]
                                parsemetype = VID
                            intpositions = getintpositions(mwenodes)
                            mweid = getmweid(
                                zichnode, svpnodes, partnode, verb, wwsvpnode, iavnode)
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
                                headlemma,
                                deepcopy(classes),
                                parsemetype,
                            )
                            mwemetas.append(mwemeta)

            sesiblings = [sibling for sibling in siblings if gav(
                sibling, 'rel') == 'se']
            if len(sesiblings) == 1:
                thesesibling = sesiblings[0]
                zichnode = thesesibling
                if verb not in mwenodes:
                    mwenodes.append(verb)
                mwenodes.append(thesesibling)
                if headlemma not in irvindeplexicon:
                    classes += [IRVd]
                else:
                    classes += [IRVi]
                    parsemetype = IRV
                    intpositions = getintpositions(mwenodes)
                    mweid = getmweid(zichnode, svpnodes,
                                     partnode, verb, wwsvpnode, iavnode)
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
                        headlemma,
                        deepcopy(classes),
                        parsemetype,
                    )
                    mwemetas.append(mwemeta)
            elif len(sesiblings) > 1:   # should not occur
                print(f'Multiple se  encountered in {sentenceid}:{sentence}')

            pcsiblings = [sibling for sibling in siblings if gav(
                sibling, 'rel') == 'pc']
            if len(pcsiblings) == 1:
                thepcsibling = pcsiblings[0]
                classes += [IAV]
                parsemetype = VID if IRVd in classes and IAV in classes else IAV
                if verb not in mwenodes:
                    mwenodes.append(verb)
                if terminal(thepcsibling):
                    mwenodes.append(thepcsibling)
                    iavnode = thepcsibling
                else:
                    siblinghead = getheadof(thepcsibling)
                    mwenodes.append(siblinghead)
                    iavnode = siblinghead
                intpositions = getintpositions(mwenodes)
                mweid = getmweid(zichnode, svpnodes, partnode,
                                 verb, wwsvpnode, iavnode)
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
                    headlemma,
                    deepcopy(classes),
                    parsemetype,
                )
                mwemetas.append(mwemeta)

    # omzetsels
    vzs = syntree.xpath(
        './/node[@pt="vz" and @rel="hd" ]'
    )  # no condition on vztype because of 'ergens op af'
    for vz in vzs:
        vzposition = int(gav(vz, "end"))
        vzazsiblings = vz.xpath(
            '../node[@pt="vz" and @vztype="fin" and @rel="hdf"]')
        for az in vzazsiblings:
            vzlemma = gav(vz, "lemma")
            azlemma = gav(az, "lemma")
            mweid = f"{vzlemma}...{azlemma}"
            azposition = int(gav(az, "end"))
            intpositions = sorted([vzposition, azposition])
            headposition = vzposition
            headpos = gav(vz, "pt")
            headlemma = gav(vz, 'lemma')
            classes = [PID]
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
                headlemma,
                deepcopy(classes),
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
