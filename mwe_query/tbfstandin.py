"""
This module is a temporary stand-in for functions that should be updated in sastadev.treebankfunctions.
These functions have been updated there, but no new package has been released yet

"""

from typing import List
from sastadev.treebankfunctions import getattval, getattval_fallback
from sastadev.sastatypes import SynTree

space = " "


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
        sortedresultlist = sorted(
            cleanresultlist, key=lambda x: int(getattval_fallback(x, "end", "9999"))
        )
        return sortedresultlist


def getyield(syntree: SynTree) -> List[str]:
    nodelist = getnodeyield(syntree)
    wordlist = [getattval(node, "word") for node in nodelist]
    return wordlist


def getyieldstr(stree: SynTree) -> str:
    theyield = getyield(stree)
    theyieldstr = space.join(theyield)
    return theyieldstr
