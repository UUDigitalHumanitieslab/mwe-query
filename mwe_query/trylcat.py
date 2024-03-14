from .lcat import getlcat
from lxml import etree

inodestrings = []
inodestrings += [
    (
        1,
        '<node begin="21" buiging="met-e" end="22" graad="basis" id="38" lemma="klaar" naamval="stan" pos="adj" positie="prenom" postag="ADJ(prenom,basis,met-e,stan)" pt="adj" rel="mod" root="klaar" word="Klare"/>',
    )
]
inodestrings = [
    (
        2,
        '<node begin="10" end="11" getal="getal" id="19" index="1" lemma="die" naamval="stan" pdtype="pron" persoon="persoon" pos="pron" postag="VNW(betr,pron,stan,vol,persoon,getal)" pt="vnw" rel="rhd" root="die" status="vol" vwtype="betr" word="die"/>',
    )
]
inodestrings = [
    (
        3,
        '<node begin="3" buiging="zonder" end="4" frame="fixed_part([tuk])" graad="basis" id="5" lcat="fixed" lemma="tuk" pos="fixed" positie="vrij" postag="ADJ(vrij,basis,zonder)" pt="adj" rel="svp" root="tuk" sense="tuk" word="tuk"/>',
    )
]

inodetrees = [(i, etree.fromstring(nodestring)) for (i, nodestring) in inodestrings]

for i, node in inodetrees:
    result = getlcat(node)
    print(i, result)
