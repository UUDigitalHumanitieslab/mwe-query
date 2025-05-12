from typing import List
from .pronadvs import metmeetottoe
from .adpositions import vzandprts
from .celexlexiconstandin import getforms
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav, showtree
import itertools
from lxml import etree as ET

rwqdebug = False


def getprepprtsubnodes(node: SynTree, alllemmanodes: List[SynTree]) -> SynTree:
    """
    creates a list of subnodes for a node for a verb that is not a particleverb
    presupposes that there are no adpositions in the majorlemmanodes
    Args:
        node: a node with pt == 'ww' and no '_' in the lemma
        alllemmanodes: all nodes in the mwe with a lemma

    Returns:

    """
    subnodes = []
    alllemmapts = [
        (gav(alllemmanode, "lemma"), gav(alllemmanode, "pt"))
        for alllemmanode in alllemmanodes
    ]
    vzlemmapts = [
        (lemma, pt) for (lemma, pt) in alllemmapts if pt == "vz" and lemma in vzandprts
    ]
    wwlemmapt = (gav(node, "lemma"), gav(node, "pt"))
    theproduct = itertools.product(vzlemmapts, [wwlemmapt])
    for vzlemmapt, wwlemmapt in theproduct:
        vzlemma, vzpt = vzlemmapt
        wwlemma, wwpt = wwlemmapt
        azlemma = metmeetottoe(vzlemma)

        prtwwlemma1 = f"{azlemma}_{wwlemma}"
        prtwwlemma2 = f"{azlemma}{wwlemma}"
        lemmavalue = f"{prtwwlemma1}|{prtwwlemma2}"
        subnode = ET.Element("subnode", {"lemma": lemmavalue})
        subnodes.append(subnode)

    return subnodes


def getotherlemmasubnodes(node: SynTree) -> List[SynTree]:
    subnodes = []
    lemma, pt = (gav(node, "lemma"), gav(node, "pt"))
    words = getforms(lemma, pt)
    if words == set():
        subnode = ET.Element("subnode", {"lemma": lemma})
        subnodes.append(subnode)
        adaptedlemma = lemma.replace("_", "")
        subnode = ET.Element("subnode", {"word": adaptedlemma})
        subnodes.append(subnode)
    else:
        wordvalue = "|".join(words)
        subnode = ET.Element("subnode", {"word": wordvalue})
        subnodes.append(subnode)
    return subnodes


def getrwqnode(
    node: SynTree, majorlemmanodes: List[SynTree], alllemmanodes: List[SynTree]
) -> SynTree:
    if node.tag != "node":
        newnode = ET.Element(node.tag, node.attrib)
        newchildren = [
            getrwqnode(child, majorlemmanodes, alllemmanodes) for child in node
        ]
        newnode.extend(newchildren)
        result = newnode
    else:
        origavdict = {
            att: node.attrib[att] for att in ["lemma", "pt"] if att in node.attrib
        }
        origsubnode = ET.Element("subnode", origavdict)
        otherlemmasubnodes = getotherlemmasubnodes(node)
        prepprtsubnodes = (
            getprepprtsubnodes(node, alllemmanodes) if gav(node, "pt") == "ww" else []
        )
        subnodes = [origsubnode] + otherlemmasubnodes + prepprtsubnodes
        if subnodes == []:
            result = node
        else:
            localtatts = ["polarity", "axis"]
            avdict = {att: node.attrib[att] for att in localtatts if att in node.attrib}
            localtnode = ET.Element("localt", avdict)
            localtnode.extend(subnodes)
            result = localtnode
    if rwqdebug:
        showtree(result, "getrwqnode: localtnode")
    return result
