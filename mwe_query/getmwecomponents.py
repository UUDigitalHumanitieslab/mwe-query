from .canonicalform import expandaltvals, tree2xpath
from sastadev.sastatypes import SynTree, Tuple
from sastadev.treebankfunctions import getattval as gav
from typing import List
from lxml import etree

Relation = str
Xpath = str
Axis = str

childaxis = "child"

altcomplpprels = ['pc', 'ld', 'predc', 'svp']
altmodpprels = ['mod', 'predm']


def getmwecomponents(
    matchingnodes: List[SynTree], mwestructures: List[SynTree]
) -> List[List[SynTree]]:
    componentslist = []
    for mweparse in mwestructures:
        mwecompsxpathexprs = getcompsxpaths(mweparse)
        for matchingnode in matchingnodes:
            components = []
            for mwecompsxpathexpr in mwecompsxpathexprs:
                try:
                    # multiple for cases such as mwu[hand in hand]
                    newcomponents = matchingnode.xpath(mwecompsxpathexpr)
                except etree.XPathEvalError:
                    print(
                        f'Xpath error. Xpath expression =:\n{mwecompsxpathexpr}')
                    print('for mweparse\n ')
                    etree.dump(mweparse)
                    exit(-1)
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


def oldgetcompsxpaths(stree: SynTree) -> List[Xpath]:
    results = []
    comps = getcomps(stree, [])
    for lstree, fpath in comps:
        lxpath = tree2xpath(lstree)
        lfpath = mkfxpath(fpath)
        xpathresult = mkxpath(lxpath, lfpath)
        results.append(xpathresult)
    return results


def getcomps(stree: SynTree, fpath: List[SynTree]) -> List[Tuple[SynTree, List[Tuple[Axis, SynTree]]]]:
    results = []
    if iscomponent(stree):
        results = [(stree, fpath)]
    else:
        for child in stree:
            axis = child.attrib["axis"] if "axis" in child.attrib else childaxis
            childresults = getcomps(child, fpath + [(axis, child)])
            results += childresults
    return results


def oldgetcomps(stree: SynTree, fpath: List[Relation]) -> List[Tuple[SynTree, List[Tuple[Axis, Relation]]]]:
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


def newgetcomps(stree: SynTree, fpath: List[Relation]) -> \
        List[Tuple[SynTree, List[Tuple[Axis, Relation]], List[SynTree]]]:
    results = []
    if iscomponent(stree):
        results = [(stree, fpath, [])]
    else:
        for child in stree:
            chrel = gav(child, "rel")
            axis = child.attrib["axis"] if "axis" in child.attrib else childaxis
            childresults = getcomps(child, fpath + [(axis, chrel)])
            results += childresults
    return results


def mkfxpath(fpath: List[Tuple[Axis, SynTree]]) -> Xpath:
    nodelist = []
    # we skip the last one because that is the node we look for
    for axis, stree in fpath[:-1]:
        axisstr = f"{axis}::" if axis != childaxis else ""
        newnode = tree2xpath(stree, alt="|")
        newnodewithaxis = f"{axisstr}{newnode}"
        nodelist.append(newnodewithaxis)
    result = "/".join(nodelist)
    return result


def oldmkfxpath(fpath: List[Tuple[Axis, Relation, ]]) -> Xpath:
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


def getaltrelcond(rel: Relation) -> str:
    if rel in altcomplpprels:
        altrels = [r for r in altcomplpprels if r != rel]
        altrelconds = getaltrelcondlist(rel, altrels + altmodpprels)
    elif rel in altmodpprels:
        altrels = [r for r in altmodpprels if r != rel]
        altrelconds = getaltrelcondlist(rel, altrels)
    else:
        altrelconds = []
    all_relconds = [f'node[@rel="{rel}"]'] + altrelconds
    result = ' or \n'.join(all_relconds)
    return result


def getdonerelscond(donerels: List[Relation]) -> str:
    result = ' or '.join([f'@rel={donerel}' for donerel in donerels])
    return result


def getaltrelcondlist(rel: Relation, altrels: List[Relation]) -> List[str]:
    results = []
    donerels = [rel]
    for altrel in altrels:
        donerelscond = getdonerelscond(donerels)
        newcond = f'(not(node[{donerelscond}]) and node[@rel="{altrel}"])'
        results.append(newcond)
        donerels.append(altrel)
    return results
