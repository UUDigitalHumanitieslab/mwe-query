from pronadvs import rvz
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav
from typing import Optional


def findiav(mwetree: SynTree, match: SynTree) -> Optional[SynTree]:
    """
    tries to find the node that matches with the MWE component marked as IAV
    Args:
        mwetree:
        match:

    Returns:

    """

    # iavmwenode = find1(mwetree, './node[@rel="pc|ld|mod|predc|svp|predm" and @cat="pp" and count(node[@pt or @cat]) = 1]/node[@rel="hd" and @pt="vz"]')
    iavmwenodes = mwetree.xpath(
        './node[ @cat="pp" and count(node[@pt or @cat]) = 1]/node[@rel="hd" and @pt="vz"]')
    iavmwenodes += mwetree.xpath(
        './node[@cat="ap"]/node[ @cat="pp" and count(node[@pt or @cat]) = 1]/node[@rel="hd" and @pt="vz"]')
    iavmatchnodes = match.xpath(
        './node[@rel="pc" and (@cat="pp" or @cat="advp")]/node[@rel="hd" and (@pt="vz" )]')
    iavmatchnodes += match.xpath(
        './node[@rel="mod" and (@cat="pp" or @cat="advp")]/node[@rel="hd" and (@pt="vz")]')
    iavmatchnodes += match.xpath(
        './node[@cat="ap" and @rel="predc"]/node[ @cat="pp" and @rel="pc"]/node[@rel="hd" and @pt="vz"]')
    for iavmwenode in iavmwenodes:
        for iavmatchnode in iavmatchnodes:
            if iavmwenode is not None:
                vzmwelemma = gav(iavmwenode, 'lemma')
                if iavmatchnode is not None:
                    vzmatchlemma = gav(iavmatchnode, 'lemma')
                    if vzmatchlemma == vzmwelemma or vzmatchlemma in rvz(vzmwelemma):
                        return iavmatchnode
    return None


basicmodpp = 'node[@rel="mod" and (@cat="pp" or @cat="advp")]/node[@rel="hd" and (@pt="vz" or @pt="bw")]'
modppinnp = f'node[@rel="obj1"]/{basicmodpp}'
pcmodiavxpath = './node[@rel="mod|pc" and @cat="pp" and count(node[@pt or @cat]) = 1]/node[@rel="hd" and @pt="vz"]'
# anyppiavxpath = './node[@cat="pp" and count(node[@pt or @cat]) = 1]/node[@rel="hd" and @pt="vz"]'
pciavxpath = './node[@rel="pc" and (@cat="pp" or @cat="advp")]/node[@rel="hd" and (@pt="vz" or @pt="bw")]'
modiavxpath = f'./{basicmodpp}'
ppinnpiavxpath = f'./{modppinnp}'
ppinnpinppxpath = f'./node[(@rel="predc" or @rel="ld" or @rel="svp" or @rel="mod" and @cat="pp")]/{modppinnp}'


def findlvciavnode(mwetree: SynTree, match: SynTree) -> Optional[SynTree]:
    iavmwenodes = mwetree.xpath(pcmodiavxpath)
    # iavmwenodes += mwetree.spath(anyppiavxpath)
    iavmwenodes += mwetree.xpath(ppinnpiavxpath)
    iavmwenodes += mwetree.xpath(ppinnpinppxpath)
    iavmatchnodes = match.xpath(pciavxpath)
    iavmatchnodes += match.xpath(modiavxpath)
    iavmatchnodes += match.xpath(ppinnpiavxpath)
    iavmatchnodes += match.xpath(ppinnpinppxpath)
    for iavmwenode in iavmwenodes:
        vzmwelemma = gav(iavmwenode, 'lemma')
        for iavmatchnode in iavmatchnodes:
            if iavmatchnode is not None:
                vzmatchlemma = gav(iavmatchnode, 'lemma')
                if vzmatchlemma == vzmwelemma or vzmatchlemma in rvz(vzmwelemma):
                    return iavmatchnode
    return None
