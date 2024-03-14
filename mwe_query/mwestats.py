import os
from typing import cast, Dict, IO, Iterable, List, Tuple
from .tbfstandin import getyieldstr
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import (
    getattval as gav,
    getstree,
    getheadof,
    getsentence,
)
from .canonicalform import (
    expandaltvals,
    generatemwestructures,
    tree2xpath,
    mknearmissstructs,
    listofsets2setoflists,
)
from .mwetyping import NodeSet
import copy
from lxml import etree

noneval = "@@NA@@"


underscore = "_"
compoundsep = underscore

cmwe = 0
cnearmiss = 1
cmissed = 2
queryresulttypes = [cmwe, cnearmiss, cmissed]

headrels = ["hd", "whd", "rhd", "cnj", "nucl"]


Relation = str
Xpath = str
Axis = str

space = " "
slash = "/"
relcatsep = slash

compsep = ";"
outsep = ":"

sentencexpath = ".//sentence/text()"


# it is not 100% clear that whd and rhd should have  lower value than body, though it seems the most appropriate here
caheads = {
    "hd": 1,
    "cmp": 2,
    "crd": 3,
    "dlink": 4,
    "body": 7,
    "rhd": 5,
    "whd": 6,
    "nucl": 8,
}

argrels = ["su", "obj1", "pobj1", "obj2", "se", "vc", "predc", "ld"]
argrelorder = {rel: i for i, rel in enumerate(argrels)}
modrels = ["mod", "predm", "obcomp", "app", "me"]
detrels = ["det"]


componentsheader = ["clemmas", "cwords", "utt", "id"]
argheader = ["rel", "arglemma", "argword", "arg", "utt", "id"]
argrelcatheader = ["rel", "cat", "utt", "id"]
argframeheader = ["argframe", "utt", "id"]
detheader = [
    "clemma",
    "detrel",
    "detcat",
    "detheadcat",
    "detheadlemma",
    "detheadword",
    "detfringe",
    "utt",
    "id",
]
modheader = [
    "clemma",
    "modrel",
    "modcat",
    "modheadcat",
    "modheadlemma",
    "modheadword",
    "modfringe",
    "utt",
    "id",
]

childaxis = "child"


class MWEcsv:
    def __init__(self, header: List[str], data: List[List[str]]):
        self.header = header
        self.data = data


# TODO: move back to SASTADEV
def getnodeyield(syntree: SynTree) -> List[SynTree]:
    resultlist = []
    if syntree is None:
        return []
    else:
        for node in syntree.iter():
            if "pt" in node.attrib or "pos" in node.attrib:
                resultlist.append(node)
        sortedresultlist = sorted(
            resultlist, key=lambda x: int(getatt_or_from_parents(x, "end", "9999"))
        )
        return sortedresultlist


def canbeabsent(node: SynTree) -> bool:
    result = gav(node, "rel") == "svp"
    return result


def getatt_or_from_parents(node: SynTree, att: str, fallback: str = "") -> str:
    """Gets the attribute from the current node or goes up in parents to find it

    Args:
        node (SynTree): node to search
        att (str): attribute name
        fallback (str): if nothing is found

    Returns:
        str: attribute value or fallback value if none is found
    """
    while True:
        if node is None:
            return fallback
        val = gav(node, att)
        if val:
            return val
        parent = node.getparent()
        if parent is None:
            return fallback
        node = parent


def removeud(stree):
    newstree = copy.deepcopy(stree)
    udnodes = newstree.xpath(".//ud")
    udnodes += newstree.xpath(".//root")
    udnodes += newstree.xpath(".//conllu")
    for udnode in udnodes:
        parent = udnode.getparent()
        parent.remove(udnode)
    return newstree


def iscomponent(stree: SynTree) -> bool:
    result = "lemma" in stree.attrib
    return result


def oldgetcomps(
    stree: SynTree, fpath: List[Relation]
) -> List[Tuple[SynTree, List[Relation]]]:
    results = []
    if iscomponent(stree):
        results = [(stree, fpath)]
        # if isparticleverb(stree):
        #    particle = getparticlenode(stree)
        #    results += [(particle, fpath)]
    else:
        for child in stree:
            chrel = gav(child, "rel")
            childresults = getcomps(child, fpath + [chrel])
            results += childresults
    return results


def getcomps(
    stree: SynTree, fpath: List[Relation]
) -> List[Tuple[SynTree, List[Tuple[Axis, Relation]]]]:
    results = []
    if iscomponent(stree):
        results = [(stree, fpath)]
        # if isparticleverb(stree):
        #    particle = getparticlenode(stree)
        #    results += [(particle, fpath)]
    else:
        for child in stree:
            chrel = gav(child, "rel")
            axis = child.attrib["axis"] if "axis" in child.attrib else childaxis
            childresults = getcomps(child, fpath + [(axis, chrel)])
            results += childresults
    return results


def shownode(stree):
    poscat = gav(stree, "cat") if "cat" in stree.attrib else gav(stree, "pt")
    id = gav(stree, "id")
    lemma = gav(stree, "lemma")
    rel = gav(stree, "rel")
    result = f"{id}: {rel}/{poscat} {lemma}"
    return result


def expandalternatives(stree: SynTree) -> List[SynTree]:
    # etree.dump(stree)
    # print(f'-->expand: {shownode(stree)}')
    newchildlistofsets = []
    for child in stree:
        if child.tag == "alternatives":
            for alternative in child:
                newalternatives = expandalternatives(alternative)
                newchildlistofsets.append(newalternatives)
        else:
            newchildalts = expandalternatives(child)
            newchildlistofsets.append(newchildalts)

    newchildsetoflists = listofsets2setoflists(newchildlistofsets)
    results = []
    if newchildsetoflists == []:
        newstree = copy.copy(stree)
        results.append(newstree)

    for newchildlist in newchildsetoflists:
        newstree = copy.copy(stree)
        # delete all the children
        for child in newstree:
            newstree.remove(child)
        # add all the new children
        for newchild in newchildlist:
            newstree.append(newchild)
        results.append(newstree)

    # print('<--Results:')
    # for atree in results:
    #     etree.dump(atree)
    return results


def oldgetcompsxpaths(stree: SynTree) -> List[Xpath]:
    results = []
    comps = getcomps(stree, [])
    for lstree, fpath in comps:
        lxpath = tree2xpath(lstree)
        lfpath = mkfxpath(fpath)
        xpathresult = mkxpath(lxpath, lfpath)
        results.append(xpathresult)
    return results


def getcompsxpaths(stree: SynTree) -> List[Xpath]:
    results = []
    comps = getcomps(stree, [])
    for lstree, fpath in comps:
        lxpath = tree2xpath(lstree)
        lfpath = mkfxpath(fpath)
        xpathresult = mkxpath(lxpath, lfpath)
        results.append(xpathresult)
    return results


def mkxpath(lxpath: Xpath, lfpath: Xpath):
    core = lxpath if lfpath == "" else f"{lfpath}/{lxpath}"
    result = f"./{core}"
    return result


def oldmkfxpath(fpath: List[Relation]) -> Xpath:
    nodelist = [
        f'node[{expandaltvals("@rel", rel,"=")}]' if rel != "" else "node"
        for rel in fpath[:-1]
    ]  # we skip the last one because that is the node we look for
    result = "/".join(nodelist)
    return result


def mkfxpath(fpath: List[Tuple[Axis, Relation]]) -> Xpath:
    nodelist = []
    for axis, rel in fpath[
        :-1
    ]:  # we skip the last one because that is the node we look for
        axisstr = f"{axis}::" if axis != childaxis else ""
        newnode = f'node[{expandaltvals("@rel", rel,"=")}]' if rel != "" else "node"
        newnodewithaxis = f"{axisstr}{newnode}"
        nodelist.append(newnodewithaxis)
    result = "/".join(nodelist)
    return result


def getargnodes(
    mwenode: SynTree, compnodes: List[SynTree], rellist=[]
) -> List[Tuple[List[Relation], SynTree]]:
    argnodes = []
    for child in mwenode:
        childrel = gav(child, "rel")
        if isarg(child):
            if child not in compnodes and not contains(child, compnodes):
                argnodes.append((rellist, child))
            else:
                newrellist = rellist + [childrel]
                deeperargs = getargnodes(child, compnodes, newrellist)
                argnodes += deeperargs
    return argnodes


def isdetarg(node) -> bool:
    rel = gav(node, "rel")
    cat = gav(node, "cat")
    hdnode = getheadof(node)
    pt = gav(hdnode, "pt")
    vwtype = gav(hdnode, "vwtype")
    bezvnw = pt == "vnw" and vwtype == "bez"
    bezvnwdetp = cat == "detp" and bezvnw
    result = rel == "det" and (cat == "np" or bezvnwdetp)
    return result


def isarg(node: SynTree) -> bool:
    rel = gav(node, "rel")
    result = rel in argrels or (rel == "svp" and "cat" in node.attrib) or isdetarg(node)
    return result


def contains(stree: SynTree, compnodes: List[SynTree]) -> bool:
    for node in stree.iter():
        if node in compnodes:
            return True
    return False


def getheads(node: SynTree) -> List[SynTree]:
    heads = []
    curhead = None
    currelrank = 10
    if gav(node, "cat") == "mwu" or "word" in node.attrib:
        heads = [node]
    else:
        for child in node:
            chrel = gav(child, "rel")
            if chrel in ["hd", "crd"]:
                heads.append(child)
            elif chrel in ["cnj"]:
                heads += getheads(child)
            elif chrel in caheads:
                chrelrank = caheads[chrel]
                if chrelrank < currelrank:
                    currelrank = chrelrank
                    curhead = child
                else:
                    pass
            else:
                pass
        if curhead is not None:
            if gav(curhead, "cat") == "mwu" or "word" in node.attrib:
                heads.append(curhead)
            else:
                heads += getheads(curhead)
    return heads


def getposcat(node):
    if "pt" in node.attrib:
        result = gav(node, "pt")
    elif "cat" in node.attrib:
        result = gav(node, "cat")
    elif "pos" in node.attrib:
        result = f'pos: {gav(node, "pos")}'
    else:
        result = "??"
    return result


Frame = List[Tuple[str, str]]


def sortframerank(relcat: Tuple[str, str]):
    rel, cat = relcat
    rellist = rel.split(slash)
    if rellist != []:
        majorrel = rellist[0]
    else:
        majorrel = rel
    rank = argrelorder[majorrel]
    return rank


def sortframe(frame: Frame) -> Frame:
    sortedframe = sorted(frame, key=lambda x: sortframerank(x))
    return sortedframe


def showrelcat(relcat: Tuple[str, str]) -> str:
    rel, cat = relcat
    result = f"{rel}{relcatsep}{cat}"
    return result


def showframe(frame: Frame) -> str:
    resultlist = [showrelcat(relcat) for relcat in frame]
    result = "[" + ", ".join(resultlist) + "]"
    return result


def ismodnode(node: SynTree, compnodes: List[SynTree]) -> bool:
    rel = gav(node, "rel")
    result = rel in modrels and not contains(node, compnodes)
    return result


def isdetnode(node: SynTree, compnodes: List[SynTree]) -> bool:
    rel = gav(node, "rel")
    result = rel in detrels and not contains(node, compnodes)
    return result


def displaystats(label: str, modstats: MWEcsv, outfile: IO):
    print(f"\n{label}:", file=outfile)
    print(outsep.join(modstats.header), file=outfile)
    rows = list(outsep.join(row).strip() for row in modstats.data)
    rows.sort()
    for row in rows:
        print(row, file=outfile)


class MWEstats:
    def __init__(
        self,
        compliststats: MWEcsv,
        argrelcatstats: MWEcsv,
        argframestats: MWEcsv,
        argstats: MWEcsv,
        modstats: MWEcsv,
        detstats: MWEcsv,
        compnodes: List[SynTree],
    ):
        self.compliststats = compliststats
        self.argrelcatstats = argrelcatstats
        self.argframestats = argframestats
        self.argstats = argstats
        self.modstats = modstats
        self.detstats = detstats
        self.compnodes = compnodes


class FullMWEstats:
    def __init__(
        self, mwestats: MWEstats, nearmissstats: MWEstats, diffstats: MWEstats
    ):
        self.mwestats = mwestats
        self.nearmissstats = nearmissstats
        self.diffstats = diffstats


class MweHitInfoDetails:
    def __init__(self, marked_utt: str):
        self.marked_utt = marked_utt


class MweHitComponents(MweHitInfoDetails):
    def __init__(self, mwe_hit: SynTree, xpath_exprs: Iterable[Xpath], tree: SynTree):
        (lemmastr, wordstr, markeduttstr), allcompnodes = updatecomponents(
            mwe_hit, xpath_exprs, tree
        )
        super().__init__(markeduttstr)
        self.nodes = allcompnodes
        self.lemma_parts = lemmastr
        self.word_parts = wordstr
        self.marked_utt = markeduttstr


class MweHitArgumentFrame(MweHitInfoDetails):
    def __init__(self, frame: Frame, tree: SynTree):
        self.frame = frame
        sortedargframe = sortframe(frame)
        sortedargframe2 = [f"{rel}/{poscat}" for (rel, poscat) in sortedargframe]
        argframetuple = tuple(sortedargframe2)
        self.frame_str = "+".join(argframetuple)
        marked_utt = getmarkedutt(tree, [])

        super().__init__(marked_utt)


class MweHitArgumentHead(MweHitInfoDetails):
    def __init__(self, rel_cat: "MweHitArgumentRelCat", hdnode: SynTree):
        super().__init__(rel_cat.marked_utt)

        if gav(hdnode, "cat") == "mwu":
            hdword = getyieldstr(hdnode)
            hdlemmalist = [gav(n, "lemma") for n in getnodeyield(hdnode)]
            hdlemma = space.join(hdlemmalist)
        else:
            hdword = gav(hdnode, "word")
            hdlemma = gav(hdnode, "lemma")

        self.rel = rel_cat.rel
        self.hdlemma = hdlemma
        self.hdword = hdword
        self.fringe = rel_cat.fringe
        self.marked_utt = rel_cat.marked_utt


class MweHitArgumentModification(MweHitInfoDetails):
    def __init__(
        self,
        comp_lemma: str,
        node_rel: str,
        node_cat: str,
        head_pos_cat: str,
        head_lemma: str,
        head_word: str,
        fringe: str,
        marked_utt: str,
    ):
        super().__init__(marked_utt)
        self.comp_lemma = comp_lemma
        self.node_rel = node_rel
        self.node_cat = node_cat
        self.head_pos_cat = head_pos_cat
        self.head_lemma = head_lemma
        self.head_word = head_word
        self.fringe = fringe


class MweHitArgumentDeterminations(MweHitInfoDetails):
    def __init__(
        self,
        comp_lemma: str,
        node_rel: str,
        node_cat: str,
        head_pos_cat: str,
        head_lemma: str,
        head_word: str,
        fringe: str,
        marked_utt: str,
    ):
        super().__init__(marked_utt)
        self.comp_lemma = comp_lemma
        self.node_rel = node_rel
        self.node_cat = node_cat
        self.head_pos_cat = head_pos_cat
        self.head_lemma = head_lemma
        self.head_word = head_word
        self.fringe = fringe


class MweHitArgumentRelCat(MweHitInfoDetails):
    def __init__(self, rellist: List[Relation], argnode: SynTree, tree: SynTree):
        basicrel = gav(argnode, "rel")
        self.rel = slash.join(rellist + [basicrel])
        self.poscat = getposcat(argnode)
        poslist = getwordposlist(argnode)
        marked_utt = getmarkedutt(tree, poslist)
        self.fringe = getyieldstr(argnode)
        super().__init__(marked_utt)

        hdnodes = getheads(argnode)
        self.heads: List[MweHitArgumentHead] = []
        for hdnode in hdnodes:
            self.heads.append(MweHitArgumentHead(self, hdnode))


class MweHitInfo:
    def __init__(self, mwe_hit: SynTree, xpath_exprs: Iterable[Xpath], tree: SynTree):
        self.components = MweHitComponents(mwe_hit, xpath_exprs, tree)
        self.arguments = MweHitArguments(mwe_hit, self.components.nodes, tree)
        self.modifications = updatemodstats(self.components.nodes, tree)
        self.determinations = updatedetstats(self.components.nodes, tree)


def getfnelements(fullname: str) -> Tuple[str, str, str]:
    path, filename = os.path.split(fullname)
    basefilename, ext = os.path.splitext(filename)
    result = (path, basefilename, ext)
    return result


def gettreebank(filenames: List[str], filenameid=False) -> Dict[str, SynTree]:
    results: Dict[str, SynTree] = {}
    for filename in filenames:
        fullstree = getstree(filename)
        if fullstree is not None:
            rawstree = fullstree.getroot()
            stree = removeud(rawstree)
            # etree.dump(stree)
            if filenameid:
                fnelements = getfnelements(filename)
                mweid = fnelements[1]
            else:
                sent = stree.xpath(sentencexpath)[0]
                mweid = sent
            results[mweid] = stree
    return results


def removeduplicatenodes(nodelist: List[SynTree]) -> List[SynTree]:
    resultlist = []
    seenspans = set()
    for node in nodelist:
        (b, e) = (gav(node, "begin"), gav(node, "end"))
        if (b, e) not in seenspans:
            resultlist.append(node)
            seenspans.add((b, e))
    return resultlist


def getstats(
    mwe: str,
    queryresults: Dict[str, List[Tuple[NodeSet, NodeSet, NodeSet]]],
    treebank: Dict[str, SynTree],
) -> FullMWEstats:
    rawmwestructures = generatemwestructures(mwe)
    mwestructures = [
        newstree for stree in rawmwestructures for newstree in expandalternatives(stree)
    ]
    # for mwestructure in mwestructures:
    #    etree.dump(mwestructure)
    # allcompnodes = []
    # mwestatslist = []
    compliststats: Dict[int, MWEcsv] = {}
    for qrt in queryresulttypes:
        compliststats[qrt] = MWEcsv(componentsheader, [])
    argrelcatstats: Dict[int, MWEcsv] = {}
    for qrt in queryresulttypes:
        argrelcatstats[qrt] = MWEcsv(argrelcatheader, [])
    argframestats: Dict[int, MWEcsv] = {}
    for qrt in queryresulttypes:
        argframestats[qrt] = MWEcsv(argframeheader, [])
    argstats: Dict[int, MWEcsv] = {}
    for qrt in queryresulttypes:
        argstats[qrt] = MWEcsv(argheader, [])
    modstats: Dict[int, MWEcsv] = {}
    for qrt in queryresulttypes:
        modstats[qrt] = MWEcsv(modheader, [])
    detstats: Dict[int, MWEcsv] = {}
    for qrt in queryresulttypes:
        detstats[qrt] = MWEcsv(detheader, [])
    allcompnodes: Dict[int, List[SynTree]] = {}
    for qrt in queryresulttypes:
        allcompnodes[qrt] = []

    for mweparse in mwestructures:
        mwecompsxpathexprs = [getcompsxpaths(mweparse)]
        nearmissstructs = mknearmissstructs([mweparse])
        nearmisscompsxpathexprs = [getcompsxpaths(stree) for stree in nearmissstructs]
        for id, resultlist in queryresults.items():
            resultcount = 0
            for mwenodes, nearmissnodes, supersetnodes in resultlist:
                resultcount += 1
                missednodes = [node for node in nearmissnodes if node not in mwenodes]
                todo: List[Tuple[NodeSet, List[List[Xpath]], int]] = [
                    (mwenodes, mwecompsxpathexprs, cmwe),
                    (nearmissnodes, nearmisscompsxpathexprs, cnearmiss),
                    (missednodes, nearmisscompsxpathexprs, cmissed),
                ]
                for rawtodonodes, xpathexprslist, qrt in todo:

                    todonodes = removeduplicatenodes(rawtodonodes)

                    for xpathexprs in xpathexprslist:
                        for mwenode in todonodes:
                            info = MweHitInfo(mwenode, xpathexprs, treebank[id])

                            # MWE Components
                            allcompnodes[qrt] = info.components.nodes
                            compliststats[qrt].data.append(
                                [
                                    info.components.lemma_parts,
                                    info.components.word_parts,
                                    info.components.marked_utt,
                                ]
                            )

                            # Arguments
                            for head in info.arguments.heads:
                                argstats[qrt].data.append(
                                    [
                                        head.rel,
                                        head.hdlemma,
                                        head.hdword,
                                        head.fringe,
                                        head.marked_utt,
                                        id,
                                    ]
                                )
                            for rel_cat in info.arguments.rel_cats:
                                argrelcatstats[qrt].data.append(
                                    [
                                        rel_cat.rel,
                                        rel_cat.poscat,
                                        rel_cat.marked_utt,
                                        id,
                                    ]
                                )
                            argframestats[qrt].data.append(
                                [
                                    info.arguments.frame.frame_str,
                                    info.arguments.frame.marked_utt,
                                    id,
                                ]
                            )

                            # Modification
                            for modification in info.modifications:
                                modstats[qrt].data.append(
                                    [
                                        modification.comp_lemma,
                                        modification.node_rel,
                                        modification.node_cat,
                                        modification.head_pos_cat,
                                        modification.head_lemma,
                                        modification.head_word,
                                        modification.fringe,
                                        modification.marked_utt,
                                        id,
                                    ]
                                )

                            # Determination
                            for determination in info.determinations:
                                detstats[qrt].data.append(
                                    [
                                        determination.comp_lemma,
                                        determination.node_rel,
                                        determination.node_cat,
                                        determination.head_pos_cat,
                                        determination.head_lemma,
                                        determination.head_word,
                                        determination.fringe,
                                        determination.marked_utt,
                                        id,
                                    ]
                                )

    newstats: Dict[int, MWEstats] = {}
    for qrt in queryresulttypes:
        newstats[qrt] = MWEstats(
            compliststats[qrt],
            argrelcatstats[qrt],
            argframestats[qrt],
            argstats[qrt],
            modstats[qrt],
            detstats[qrt],
            allcompnodes[qrt],
        )

    result = FullMWEstats(newstats[cmwe], newstats[cnearmiss], newstats[cmissed])
    return result


def getmwecomponents(
    matchingnodes: List[SynTree], mwestructures: List[SynTree]
) -> List[List[SynTree]]:
    componentslist = []
    for mweparse in mwestructures:
        mwecompsxpathexprs = getcompsxpaths(mweparse)
        for matchingnode in matchingnodes:
            components = []
            for mwecompsxpathexpr in mwecompsxpathexprs:
                newcomponents = matchingnode.xpath(
                    mwecompsxpathexpr
                )  # multiple for cases such as mwu[hand in hand]
                if newcomponents == []:
                    components = []  # because all components must be present
                    break
                for newcomponent in newcomponents:
                    if newcomponent is not None:
                        if (
                            newcomponent not in components
                        ):  # for cases suchj as hand in hand under mwu
                            components.append(newcomponent)
                            break  # as soon as we have found on we are done
                    else:
                        if not canbeabsent(newcomponent):
                            components = []  # because all components must be present
                            break
        if components != []:
            componentslist.append(components)
    return componentslist


def displayfullstats(stats: MWEstats, outfile, header=""):

    compliststats = stats.compliststats

    print(f"\n\n{header}", file=outfile)

    print("\nMWE Components:", file=outfile)
    headerstr = outsep.join(compliststats.header)
    print(headerstr, file=outfile)
    rows: List[str] = []
    for clemmas, cwords, utt in compliststats.data:
        rows.append(f"{clemmas}: {cwords}: {utt}".strip())

    rows.sort()

    for row in rows:
        print(row, file=outfile)

    argstats = stats.argstats
    print("\nArguments:", file=outfile)
    headerstr = outsep.join(argstats.header)
    print(headerstr, file=outfile)
    rows = list(outsep.join(row).strip() for row in argstats.data)
    rows.sort()
    for row in rows:
        print(row, file=outfile)

    argrelcatstats = stats.argrelcatstats
    print("\nArguments by relation and category:", file=outfile)
    headerstr = outsep.join(argrelcatstats.header)
    print(headerstr, file=outfile)
    rows = list(outsep.join(row).strip() for row in argrelcatstats.data)
    rows.sort()
    for row in rows:
        print(row, file=outfile)

    argframestats = stats.argframestats
    print("\nArgument frames:", file=outfile)
    headerstr = outsep.join(argframestats.header)
    print(headerstr, file=outfile)
    rows = list(outsep.join(row).strip() for row in argframestats.data)
    rows.sort()
    for row in rows:
        print(row, file=outfile)

    modstats = stats.modstats
    displaystats("Modification", modstats, outfile)

    detstats = stats.detstats
    displaystats("Determination", detstats, outfile)


def updatedetstats(
    allcompnodes: List[SynTree], tree: SynTree
) -> List[MweHitArgumentDeterminations]:
    detstats: List[MweHitArgumentDeterminations] = []
    for compnode in allcompnodes:
        comprel = gav(compnode, "rel")
        complemma = gav(compnode, "lemma")
        if comprel == "hd":
            compparent = compnode.getparent()
            detnodes = (
                [child for child in compparent if isdetnode(child, allcompnodes)]
                if compparent is not None
                else []
            )
            if detnodes == []:
                uttstr = getsentence(tree)
                newentry = MweHitArgumentModification(
                    complemma, noneval, noneval, noneval, noneval, noneval, "", uttstr
                )
                detstats.append(newentry)
            else:
                for detnode in detnodes:
                    detnodecat = getposcat(detnode)
                    detnoderel = gav(detnode, "rel")
                    detfringe = getyieldstr(detnode)
                    detheads = getheads(detnode)
                    poslist = getwordposlist(detnode)
                    markeduttstr = getmarkedutt(tree, poslist)
                    for dethead in detheads:
                        detheadlemma = gav(dethead, "lemma")
                        detheadword = gav(dethead, "word")
                        detheadposcat = getposcat(dethead)
                        newentry = MweHitArgumentDeterminations(
                            complemma,
                            detnoderel,
                            detnodecat,
                            detheadposcat,
                            detheadlemma,
                            detheadword,
                            detfringe,
                            markeduttstr,
                        )
                        detstats.append(newentry)
    return detstats


def updatemodstats(
    allcompnodes: List[SynTree], tree: SynTree
) -> List[MweHitArgumentModification]:
    modstats: List[MweHitArgumentModification] = []
    for compnode in allcompnodes:
        comprel = gav(compnode, "rel")
        complemma = gav(compnode, "lemma")
        if comprel == "hd":
            compparent = compnode.getparent()
            modnodes = (
                [child for child in compparent if ismodnode(child, allcompnodes)]
                if compparent is not None
                else []
            )
            if modnodes == []:
                uttstr = getsentence(tree)
                newentry = MweHitArgumentModification(
                    complemma, noneval, noneval, noneval, noneval, noneval, "", uttstr
                )
                modstats.append(newentry)
            else:
                for modnode in modnodes:
                    modnodecat = getposcat(modnode)
                    modnoderel = gav(modnode, "rel")
                    modfringe = getyieldstr(modnode)
                    modheads = getheads(modnode)
                    poslist = getwordposlist(modnode)
                    markeduttstr = getmarkedutt(tree, poslist)
                    for modhead in modheads:
                        modheadlemma = gav(modhead, "lemma")
                        modheadword = gav(modhead, "word")
                        modheadposcat = getposcat(modhead)
                        newentry = MweHitArgumentModification(
                            complemma,
                            modnoderel,
                            modnodecat,
                            modheadposcat,
                            modheadlemma,
                            modheadword,
                            modfringe,
                            markeduttstr,
                        )
                        modstats.append(newentry)
    return modstats


class MweHitArguments:
    def __init__(self, mwe_hit: SynTree, component_nodes: List[SynTree], tree: SynTree):
        argnodes = getargnodes(mwe_hit, component_nodes)
        argframe: Frame = []
        self.heads: List[MweHitArgumentHead] = []
        self.rel_cats: List[MweHitArgumentRelCat] = []
        for rellist, argnode in argnodes:
            newargrelcatstat = MweHitArgumentRelCat(rellist, argnode, tree)
            argframe.append((newargrelcatstat.rel, newargrelcatstat.poscat))
            self.rel_cats.append(newargrelcatstat)
            self.heads += newargrelcatstat.heads

        self.frame = MweHitArgumentFrame(argframe, tree)


def updatecomponents(mwenode: SynTree, xpathexprs: Iterable[str], tree: SynTree):
    allcompnodes: List[SynTree] = []
    for xpathexpr in xpathexprs:
        compnodes = mwenode.xpath(xpathexpr)
        allcompnodes += cast(Iterable[SynTree], compnodes)

    complist: List[Tuple[str, str, int]] = []
    for compnode in allcompnodes:
        word = gav(compnode, "word")
        lemma = gav(compnode, "lemma")
        pos = int(gav(compnode, "begin"))
        complist.append((lemma, word, pos))
        # print(f'{pos}: {word}')

    sortedcomplist = sorted(complist, key=lambda x: x[0])
    sortedlemmalist = [lemma for (lemma, _, _) in sortedcomplist]
    wordlist = [word for (_, word, _) in sortedcomplist]
    poslist = [pos for (_, _, pos) in sortedcomplist]
    lemmastr = compsep.join(sortedlemmalist)
    wordstr = compsep.join(wordlist)

    markeduttstr = getmarkedutt(tree, poslist)

    newentry = (lemmastr, wordstr, markeduttstr)

    return newentry, allcompnodes


def markutt(wlist: List[Tuple[int, str]], poslist: List[int]):
    result: List[str] = []
    for pos, word in wlist:
        if pos in poslist:
            newword = markword(word)
        else:
            newword = word
        result.append(newword)
    return result


def markword(w: str):
    result = f"<b>{w}</b>"
    return result


def getmarkedutt(tree: SynTree, poslist: List[int]):
    treeyield = getnodeyield(tree)
    treeyieldstrlist = [
        (int(getatt_or_from_parents(node, "begin", "9999")), gav(node, "word"))
        for node in treeyield
    ]
    markedutt = markutt(treeyieldstrlist, poslist)
    markeduttstr = space.join(markedutt)
    return markeduttstr


def getwordposlist(node: SynTree):
    wordnodes = getnodeyield(node)
    poslist = [int(gav(n, "begin")) for n in wordnodes]
    return poslist


def getheadcomponents(match: SynTree, components: List[SynTree]) -> List[SynTree]:
    headcomponents = [
        child
        for child in match
        if child in components
        and "pt" in child.attrib
        and gav(child, "rel") in headrels
    ]
    if headcomponents == []:
        for child in match:
            childheadcomponents = getheadcomponents(child, components)
            if childheadcomponents != []:
                return childheadcomponents
        return []
    else:
        return headcomponents


def getheadcomponent(match: SynTree, components: List[SynTree]) -> SynTree:

    headcomponents = getheadcomponents(match, components)
    if headcomponents == []:
        headcomponents = components
    for headcomponent in headcomponents:
        if headcomponent is None:
            print(f'"None head component for {getyieldstr(match)}')
            print("\nmatch:")
            etree.dump(match)
            exit(-1)

    sortedheadcomponents = sorted(headcomponents, key=lambda c: int(gav(c, "end")))
    headcomponent = sortedheadcomponents[0] if sortedheadcomponents != [] else None
    return headcomponent
