from typing import cast, Dict, List, Optional
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav
from .canonicalform import listofsets2setoflists
from .mwestats import getmarkedutt

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
        dirchar = dirchars[self.direction]
        resultlist = [dirchar + rel for rel in self.rellist]
        result = ''.join(resultlist)
        return result


class Gramconfig:
    def __init__(self, gramchains: List[Gramchain]):
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
            parent = cast(Optional[SynTree], node1)
            lca = node1  # lowest common ancestor
            while not contains(parent, node2):
                if parent is None:
                    break
                rel = gav(parent, 'rel')
                rellist.append(rel)
                parent = parent.getparent()
                if parent is None:
                    break
                else:
                    lca = parent

            gramchain1 = Gramchain(rellist, up)
            gramchains.append(gramchain1)

            rellist = []
            parent = node2
            while parent != lca:
                if parent is None:
                    break
                rel = gav(parent, 'rel')
                rellist.append(rel)
                parent = parent.getparent()

            revrellist = list(reversed(rellist))
            gramchain2 = Gramchain(revrellist, down)
            gramchains.append(gramchain2)

    result = Gramconfig(gramchains)
    return result


def contains(node1: Optional[SynTree], node2: Optional[SynTree]) -> bool:
    if node1 is None or node2 is None:
        return False

    for node in node1.iter('node'):
        if node == node2:
            return True

    return False


def getgramconfigstats(componentslist: List[List[str]], treebank: Dict[str, SynTree]) -> List[List[str]]:
    gramconfigstatsdata: List[List[str]] = []
    for treeid in treebank:
        tree = treebank[treeid]
        for components in componentslist:
            componentstuple = tuple(components)
            componentsnodes: List[List[SynTree]] = []
            for component in components:
                componentnodes = cast(List[SynTree], tree.xpath(f'//node[@lemma="{component}"]'))
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
