from typing import Any, Dict, List
from sastatypes import SynTree
from treebankfunctions import getattval as gav
from collections import defaultdict
from canonicalform import  listofsets2setoflists
from typefunctions import nested_dict
from mwestats import getmarkedutt

Relation = str
Direction = int

up, down = 0, 1
dirchars = r'\/'

gramconfigheader = ['ctuple', 'gramconfig', 'treeid', 'utt']

class Gramchain:
    def __init__(self, rellist: List[Relation], dir: Direction):
        self.rellist = rellist
        self.direction = dir
    def __str__(self):
        dirchar =  dirchars[self.direction]
        resultlist = [dirchar + rel for rel in self.rellist]
        result = ''.join(resultlist)
        return result

class Gramconfig:
    def __init__(self, gramchains: Gramchain):
        self.gramchains = gramchains
    def __str__(self):
        gramchainstrs = [str(gramchain) for gramchain in self.gramchains]
        result = ''.join(gramchainstrs)
        return result


def getgramconfig(nodelist: List[SynTree]) -> Gramconfig:
    sortednodelist = sorted(nodelist, key=lambda n: gav(n, 'lemma'))
    lsortednodelist = len(sortednodelist)
    gramchains = []
    for i in range(lsortednodelist):
        if i < lsortednodelist - 1:
            node1 = sortednodelist[i]
            node2 = sortednodelist[i+1]
            rellist = []
            parent = node1
            while not contains(parent, node2):
                rel = gav(parent, 'rel')
                rellist.append(rel)
                parent = parent.getparent()

            gramchain1 = Gramchain(rellist, up)
            gramchains.append(gramchain1)

            lca = parent # lowest common ancestor

            rellist = []
            parent = node2
            while parent != lca:
                rel = gav(parent, 'rel')
                rellist.append(rel)
                parent = parent.getparent()

            revrellist = list(reversed(rellist))
            gramchain2 = Gramchain(revrellist, down)
            gramchains.append(gramchain2)

    result = Gramconfig(gramchains)
    return result

def contains(node1:SynTree, node2: SynTree) -> bool:
    for node in node1.iter('node'):
        if node == node2:
            return True

    return False

def getgramconfigstats(componentslist:List[List[str]], treebank:Dict[str,SynTree]) -> List[List[Any]]:
    gramconfigstatsdata = []
    for treeid in treebank:
        tree = treebank[treeid]
        for components in componentslist:
            componentstuple = tuple(components)
            componentsnodes = []
            for component in components:
                componentnodes = tree.xpath(f'//node[@lemma="{component}"]')
                componentsnodes.append(componentnodes)

            cnodelists = listofsets2setoflists(componentsnodes)

            for cnodelist in cnodelists:
                result = getgramconfig(cnodelist)
                resultstr = str(result)
                ctuplestr = '+'.join(componentstuple)
                poslist = [int(gav(cnode, 'begin')) for cnode in cnodelist]
                utt = getmarkedutt(tree, poslist)
                newentry = [ctuplestr, resultstr, treeid, utt]
                gramconfigstatsdata.append(newentry)

    return gramconfigstatsdata
