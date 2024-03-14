from typing import List, Tuple
from sastadev.sastatypes import SynTree
from sastadev.treebankfunctions import getattval as gav
from .adpositions import allprepositions

PosTag = str

mwu_exceptiondict = {
    "noem maar op": ("ww", 1),
    "deo volente": ("ww", 2),
    "nolens volens": ("ww", 2),
    "alea iacta est": ("ww", 3),
    "linea recta": ("bw", 1),
    "een en ander": ("vnw", 1),
    "oen meloen": ("n", 1),
    "van zins": ("vz", 1),
    "geen blijf": ("n", 2),
    "hand in hand": ("vz", 2),
    "de eerste de beste": ("n", 2),
    "Olympische Spelen": ("n", 2),
    "beelden kunstenaar": ("n", 2),
    "moederziel alleen": ("adj", 2),
    "koste wat het kost": ("ww", 1),
    "koste wat kost": ("ww", 1),
    "geen snars": ("n", 2),
    "deja vuutje": ("n", 2),
    "secundum Lucam": ("vz", 1),
    "dernier cri": ("n", 2),
    "Jan en alleman": ("n", 1),
    "alles kits": ("ww", 2),
    "wee je geneente": ("ww", 1),
    "wat voor één": ("vnw", 1),
}

nameinfixes = {
    "'t",
    "de",
    "den",
    "der",
    "des",
    "'s",
    "ten",
    "ter",
    "van",
}


comma = ","
lemmaatt = "lemma"
ptatt = "pt"


def intpos(stree: SynTree) -> int:
    result = int(gav(stree, "end"))
    return result


def get_nmwuhead(sons: List[SynTree]) -> SynTree:
    for son in sons:
        sonlemma = gav(son, "lemma")
        if sonlemma not in nameinfixes:
            return son
    return sons[0]


def get_mwuprops(stree: SynTree) -> Tuple[SynTree, PosTag, int]:
    """
    it is presupposed that the input stree is of category mwu and that its has children
    Args:
        stree:

    Returns:

    """
    result = None
    lcat = gav(stree, "lcat")
    mwuroot = gav(stree, "mwu_root")
    sonpts = [gav(son, "pt") for son in stree]
    if mwuroot in mwu_exceptiondict:
        pos, headposition = mwu_exceptiondict[mwuroot]
        headnode = stree[headposition - 1]
        result = headnode, pos, headposition
    elif lcat == "pp" and sonpts[0] == "vz":
        result = stree[0], "vz", intpos(stree[0])
    elif sonpts[0] == "vz":
        result = stree[0], "vz", intpos(stree[0])
    elif gav(stree[0], "lemma") in allprepositions:
        result = stree[0], "vz", intpos(stree[0])
    elif all([sonpt == "n" for sonpt in sonpts]):
        headnode = get_nmwuhead([child for child in stree])
        result = headnode, "n", intpos(headnode)
    elif all([gav(son, "pt") == "spec" for son in stree]):
        if all([gav(son, "spectype") == "deeleigen" for son in stree]):
            headnode = get_nmwuhead([child for child in stree])
            result = headnode, "n", intpos(headnode)
        elif any([gav(son, "spectype") == "afk" for son in stree]):
            result = stree[-1], "n", intpos(stree[-1])
    elif all([(sonpt == sonpts[0] or sonpt == "vg") for sonpt in sonpts]):
        result = stree[0], sonpts[0], 1
    if result is None:
        print(
            f'Unknown mwu type: {mwuroot}: {comma.join([f"{gav(child, ptatt)}/{gav(child, lemmaatt)}" for child in stree])}'
        )
        result = stree[0], "n", 1
    return result
