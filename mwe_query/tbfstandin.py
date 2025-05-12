"""
This module is a temporary stand-in for functions that should be updated in sastadev.treebankfunctions.
These functions have been updated there, but no new package has been released yet

"""
from .constants import nospaceafter
from typing import List, Tuple
from sastadev.treebankfunctions import getattval, find1
from sastadev.sastatypes import SynTree
import copy
from lxml import etree

space = " "

udentities = ['acl', 'advcl', 'advmod', 'amod', 'appos', 'aux', 'case', 'cc', 'ccomp',
              'clf', 'compound', 'conj', 'cop', 'csubj', 'det', 'discours', 'dislocated',
              'expl', 'fixed', 'flat', 'goeswith', 'iobj', 'list', 'mark', 'nmod', 'nsubj',
              'nummod', 'obj', 'obl', 'orphan', 'parataxis', 'punct', 'ref', 'reparandum', 'ud', 'vocative', 'xcomp']


def removeduplicates(wordnodelist: List[SynTree]) -> List[SynTree]:
    resultlist = []
    donebeginendtuples = set()
    for wordnode in wordnodelist:
        (b, e) = (getattval(wordnode, "begin"), getattval(wordnode, "end"))
        if (b, e) not in donebeginendtuples:
            resultlist.append(wordnode)
            donebeginendtuples.add((b, e))
    return resultlist


def iswordnode(stree: SynTree) -> bool:
    result = 'word' in stree.attrib or 'lemma' in stree.attrib or 'pt' in stree.attrib or 'pos' in stree.attrib
    return result


def getnodeyield(syntree: SynTree) -> List[SynTree]:
    resultlist = []
    if syntree is None:
        return []
    else:
        for node in syntree.iter():
            if node.tag in ["node"] and iswordnode(node):
                if getattval(node, "pt") != "dummy":
                    resultlist.append(node)
        cleanresultlist = removeduplicates(resultlist)
        # sortedresultlist = sorted(
        #    cleanresultlist, key=lambda x: int(getattval_fallback(x, "end", "9999"))
        sortedresultlist = sorted(
            cleanresultlist, key=lambda x: getnodeposition(x))
        return sortedresultlist


def getyield(syntree: SynTree) -> List[str]:
    nodelist = getnodeyield(syntree)
    wordlist = [getattval(node, "word") for node in nodelist]
    return wordlist


def getyieldstr(stree: SynTree) -> str:
    theyield = getyield(stree)
    theyieldstr = space.join(theyield)
    return theyieldstr


def getnodeposition(node: SynTree) -> Tuple[int, int]:
    nodeend = getattval(node, 'end')
    if nodeend == '':
        nodeend = '9999'
    nodesubbegin = getattval(node, 'subbegin')
    if nodesubbegin == '':
        nodesubbegin = '0'
    nodeendint = int(nodeend)
    nodesubbeginint = int(nodesubbegin)
    result = (nodeendint, nodesubbeginint)
    return result


# tghibnk more about it , positions are tuples
def newgetyieldstr(stree: SynTree, marking=[]) -> str:
    nodes = getnodeyield(stree)
    lnodes = len(nodes)
    result = ''
    for i, node in enumerate(nodes):
        wordpos = i + 1
        word = getattval(node, 'word')
        spacing = getattval(node, 'spacing')
        if wordpos in marking:
            word = mark(word)
        if spacing == nospaceafter:
            result += word
        elif i != lnodes - 1:   # no space after the last word
            result += word
        else:
            result += f'{word} '  # normally, a word is followed by a space
    return result


def mark(wrd: str) -> str:
    result = f'*{wrd}*'
    return result


def removeud(stree: SynTree) -> SynTree:
    newstree = copy.deepcopy(stree)
    nodetags = udentities
    for nodetag in nodetags:
        udnodes = newstree.xpath(f'.//{nodetag}')
        for udnode in udnodes:
            udnodeparent = udnode.getparent()
            udnodeparent.remove(udnode)
    return newstree


def writetb(mwetreebank, mwetreebankfullname):
    tb = etree.Element("treebank")
    for el in mwetreebank:
        tb.append(mwetreebank[el])
    fulltb = etree.ElementTree(tb)
    fulltb.write(
        mwetreebankfullname, encoding="UTF8", xml_declaration=False, pretty_print=True
    )


def renumber(stree: SynTree, begin: str) -> SynTree:
    newstree = copy.deepcopy(stree)
    wordnodes = newstree.xpath('.//node[@word]')
    sortedwordnodes = sorted(
        wordnodes, key=lambda n: int(getattval(n, 'begin')))
    intbegin = int(begin)
    curintbegin = intbegin
    for wordnode in sortedwordnodes:
        curbegin = str(curintbegin)
        curend = str(curintbegin + 1)
        wordnode.set('begin', curbegin)
        wordnode.set('end', curend)
        curintbegin += 1
    updatecatnodes(newstree)
    # deal with the empty nodes
    updatebareindexnodes(newstree)
    return newstree


def updatecatnodes(stree: SynTree) -> None:
    """
    updates the begin and end attributes of phrasal nodes
    Args:
        stree:

    Returns:

    """
    for child in stree:
        if 'cat' in child.attrib:
            updatecatnodes(child)
    children = [child for child in stree]
    sortedchildren = sorted(children, key=lambda n: int(getattval(n, 'begin')))
    firstchild = sortedchildren[0]
    lastchild = sortedchildren[-1]
    newbegin = getattval(firstchild, 'begin')
    newend = getattval(lastchild, 'end')
    stree.set('begin', newbegin)
    stree.set('end', newend)


def updatebareindexnodes(syntree: SynTree) -> None:
    bareindexnodes = syntree.xpath(
        './/node[@index and not(@cat) and not(@word)]')
    for bareindexnode in bareindexnodes:
        theindex = getattval(bareindexnode, 'index')
        theantecedent = find1(
            syntree, f'.//node[(@cat or @word) and @index="{theindex}" ]')
        if theantecedent is not None:
            newbegin = getattval(theantecedent, 'begin')
            newend = getattval(theantecedent, 'end')
            bareindexnode.set('begin', newbegin)
            bareindexnode.set('end', newend)
