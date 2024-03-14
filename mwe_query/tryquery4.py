from typing import List, Tuple
from .canonicalform import coremksuperquery
from .mwetyping import Pos, Xpathexpression
from .rwq import getrwqnode
from lxml import etree

# given a lemma of a certain ptwe want to find all forms of this lemma, and
# then search for each of these forms irrespective of pt and lemma
# so verb bommen with lemma bommen also finds the word bommen as a noun
# if the lemma is not in the dictionary  we want to find all words that have lemma as prefix (as substring?)
# verb with preposition try also the preposition as a separable prefix
# can we do something with unknown words / words with wrong lemmas"Fransje/Fransje, Fransjes/Fransjes
# Gordiaanse -> Gordiaans can be dealt with


majorlemmaptslist = [
    [("kunnen", "ww"), ("bommen", "ww")],
    [("kunnen", "ww"), ("velen", "ww")],
    [("mouw", "n"), ("passen", "ww"), ("aan", "vz")],
]


def mknode(lemma, pt):
    result = etree.Element("node", attrib={"lemma": lemma, "pt": pt})
    return result


kunnenwwnode = mknode("kunnen", "ww")
bommenwwnode = mknode("bommen", "ww")
aanvznode = mknode("aan", "vz")
totvznode = mknode("tot", "vz")
latenwwnode = mknode("laten", "ww")
werkenwwnode = mknode("werken", "ww")
passenwwnode = mknode("passen", "ww")
mouwznnode = mknode("mouw", "n")
gordiaansadjnode = mknode("gordiaans", "adj")
knoopznnode = mknode("knoop", "n")
doorhakkenwwnode = mknode("door_hakken", "ww")

kunnenbommen = etree.Element("node")
kunnenbommen.extend([kunnenwwnode, bommenwwnode])
aantotlatenwerken = etree.Element("node")
aantotlatenwerken.extend([aanvznode, totvznode, latenwwnode, werkenwwnode])
mouwpassenaan = etree.Element("node")
mouwpassenaan.extend([mouwznnode, passenwwnode, aanvznode])
gordiaanseknoopdoorhakken = etree.Element("node")
gordiaanseknoopdoorhakken.extend([gordiaansadjnode, knoopznnode, doorhakkenwwnode])

mwestructs = [
    (kunnenbommen, "kunnen bommen"),
    (mouwpassenaan, "mouw passen aan"),
    (aantotlatenwerken, "aantotlatenwerken"),
    (gordiaanseknoopdoorhakken, "Gordiaanse knoop doorhakken"),
]


def mkcoremlq(lemmapts: List[Tuple[str, Pos]]) -> Xpathexpression:
    first = lemmapts[0]
    rest = lemmapts[1:]
    firstlemma, firstpt = first
    firstcondition = f'(@lemma="{firstlemma}" and @pt="{firstpt}")'
    restconditions = [
        f'ancestor::alpino_ds/node[@cat="top" and descendant::[@lemma="{rlemma}" and @pt="{rpt}"]'
        for rlemma, rpt in rest
    ]
    restexpression = "/".join(restconditions)
    result = f"node[{firstcondition}]/{restexpression}"
    return result


def testaltcoderwq():
    alllemmanodes = {}
    majorlemmanodes = {}
    alllemmanodes[1] = [kunnenwwnode, bommenwwnode]
    majorlemmanodes[1] = alllemmanodes[1]
    alllemmanodes[2] = [mouwznnode, aanvznode, passenwwnode]
    majorlemmanodes[2] = [mouwznnode, passenwwnode]
    alllemmanodes[3] = [aanvznode, totvznode, latenwwnode, werkenwwnode]
    majorlemmanodes[3] = [latenwwnode, werkenwwnode]

    for i in majorlemmanodes:
        for node in majorlemmanodes[i]:
            altnode = getrwqnode(node, majorlemmanodes[i], alllemmanodes[i])
            etree.dump(altnode)


def testrwq_query():
    for mwestruct, mwe in mwestructs:
        rwq = coremksuperquery([mwestruct], mwe, rwq=True)
        print(rwq)


if __name__ == "__main__":
    # testaltcoderwq()
    testrwq_query()
