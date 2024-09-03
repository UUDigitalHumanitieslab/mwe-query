from canonicalform import expandaltvals, tree2xpath
from sastadev.sastatypes import SynTree, Tuple
from sastadev.treebankfunctions import getattval as gav
from typing import List
from lxml import etree

Relation = str
Xpath = str
Axis = str

childaxis = "child"


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

def getcompsxpaths(stree: SynTree) -> List[Xpath]:
    results = []
    comps = getcomps(stree, [])
    for lstree, fpath in comps:
        lxpath = tree2xpath(lstree)
        lfpath = mkfxpath(fpath)
        xpathresult = mkxpath(lxpath, lfpath)
        results.append(xpathresult)
    return results

def getcomps(stree: SynTree, fpath: List[Relation]) -> List[Tuple[SynTree, List[Tuple[Axis, Relation]]]]:
    results = []
    if iscomponent(stree):
        results = [(stree, fpath)]
    else:
        for child in stree:
            chrel = gav(child, "rel")
            axis = child.attrib["axis"] if "axis" in child.attrib else childaxis
            childresults = getcomps(child, fpath + [(axis, chrel)])
            results += childresults
    return results

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

def canbeabsent(node: SynTree) -> bool:
    result = gav(node, "rel") == "svp"
    return result

def mkxpath(lxpath: Xpath, lfpath: Xpath):
    core = lxpath if lfpath == "" else f"{lfpath}/{lxpath}"
    result = f"./{core}"
    return result

def iscomponent(stree: SynTree) -> bool:
    result = "lemma" in stree.attrib
    return result

