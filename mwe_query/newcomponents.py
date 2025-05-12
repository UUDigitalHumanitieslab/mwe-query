from lxml import etree
from canonicalform import tree2xpath, mknearmissstructs
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav, nodecopy, complrels
from typing import List, Optional, Tuple
from getmwecomponents import Axis, childaxis, iscomponent, mkxpath, Xpath, Relation

doordemandvallenmweparsestr = """
<node id="4">
  <node rel="pc|ld|mod|predc|svp|predm" cat="pp" id="1" nodecount="2">
    <node lemma="door" rel="hd" pt="vz" vztype="init" id="2"/>
    <node rel="obj1" cat="np" id="3" nodecount="2">
      <node rel="det" cat="detp" nodecount="1">
        <node lemma="de|'s|den|der|des" rel="hd" pt="lid" lwtype="bep" id="4"/>
      </node>
      <node lemma="mand" rel="hd" pt="n" ntype="soort" genus="zijd" getal="ev" graad="basis" id="5"/>
    </node>
  </node>
  <node lemma="vallen" rel="hd" pt="ww" id="10"/>
</node>
"""


doordemandvallenparse = etree.fromstring(doordemandvallenmweparsestr)


def getcompsxpaths(stree: SynTree) -> List[Xpath]:
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


def mkfxpath(fpath: List[Tuple[Axis, SynTree]]) -> Xpath:
    nodelist = []
    # we skip the last one because that is the node we look for
    for axis, stree in fpath[:-1]:
        axisstr = f"{axis}::" if axis != childaxis else ""
        newnode = tree2xpath(stree)
        newnodewithaxis = f"{axisstr}{newnode}"
        nodelist.append(newnodewithaxis)
    result = "/".join(nodelist)
    return result


def containscomponent(stree: SynTree) -> bool:
    if iscomponent(stree):
        return True
    elif stree.xpath('.//node[@lemma]') != []:
        return True
    else:
        return False


def removenoncomponentphrases(stree: SynTree) -> SynTree:
    nodestoremove = []
    for node in stree.iter():
        if not containscomponent(node):
            nodestoremove.append(node)

    newtree = removenodes(stree, nodestoremove)
    return newtree


def removenodes(stree: SynTree, nodestoremove: List[SynTree]) -> Optional[SynTree]:
    newchilds = []
    for child in stree:
        newchild = removenodes(child, nodestoremove)
        if newchild is not None:
            newchilds.append(newchild)
    if stree in nodestoremove:
        return None
    else:
        newstree = nodecopy(stree)
        newstree.extend(newchilds)
        return newstree


def getnoncomplements(stree: SynTree) -> List[Relation]:
    """
    determines the complement relations that cannot occur, e.g. to avoid
    het gaat' as an MWE in 'het gaat goed' or 'het gaat om iets anders'

    The list should be transated to a condition such as f'not(node[@rel="{'|'.join(list)}"])'

    should be applied to clausal nodes, ap nodes, pp nodes (these can contauin complements)
    Args:
        stree:

    Returns:

    """
    compls = {gav(child, 'rel')
              for child in stree if gav(child, 'rel') in complrels}
    # obj1 only allowed when it is in the mwetree; its absence (topic drop) must be dealt with differently
    diff = set(complrels) - compls - {'su'}
    return list(diff)


def getnoncomplementscondition(stree: SynTree) -> str:
    notallowedcompls = getnoncomplements(stree)
    condition = ' or '.join([f'@rel == "{rel}"' for rel in notallowedcompls])
    result = f'not(node[{condition}])'
    return result


if __name__ == '__main__':
    # xpaths = getcompsxpaths(doordemandvallenparse)
    nearmiss_structs = mknearmissstructs([doordemandvallenparse])
    print('****nearmiss_structs****')
    for nearmiss_struct in nearmiss_structs:
        etree.dump(nearmiss_struct)
        cleanstruct = removenoncomponentphrases(nearmiss_struct)
        print('****cleanstruct****')
        etree.dump(cleanstruct)
    junk = 0
