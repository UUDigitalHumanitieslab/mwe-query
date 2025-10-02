"""
The module proadvs generates a list of pronominal adverb lemmas (pronadvlemmas)
and provides a function to create pronominal adverb lemmas (strings)
"""

from typing import List, Optional, Tuple
from sastadev.sastatypes import SynTree
from .stringfstandin import strip_accents

Rpronouns = ["er", "hier", "daar", "waar"]
fixedrpronouns = Rpronouns

robustrpronouns = ["d'r", "dr"]

Radpositions = [
    "aan",
    "achter",
    "af",
    "beneden",
    "bij",
    "binnen",
    "boven",
    "bovenaan",
    "buiten",
    "door",
    "doorheen",
    "in",
    "langs",
    "langsheen",
    "mee",
    "na",
    "naar",
    "naast",
    "om",
    "onder",
    "onderaan",
    "op",
    "over",
    "rond",
    "rondom",
    "tegen",
    "tegenover",
    "toe",
    "tussen",
    "uit",
    "van",
    "vanaf",
    "vanonder",
    "vanuit",
    "voor",
    "voorbij",
    "zonder",
]


circumpositions = [
    ["tussen", "in"],
    ["tegen", "aan"],
    ["van", "af"],
    ["van", "uit"],
    ["tussen", "uit"],
    ["achter", "uit"],
    # voor , uit
    ["boven", "uit"],
    ["onder", "uit"],
    # van , vandaan
    # tussen , vandaan
    # achter , vandaan
    # voor , vandaan
    # boven , vandaan
    # onder , vandaan
    # bij , vandaan
    # uit , vandaan
    ["door", "heen"],
    # langs , heen
    ["om", "heen"],
    ["over", "heen"],
    # achter , langs
    # voor , langs
    # boven , langs
    # onder , langs
    # achter , om
    # buiten , om
    ["onder", "door"],
    ["tussen", "door"],
    ["op", "af"],
    ["achter", "aan"],
    ["op", "aan"],
    ["naar", "toe"],
    # tot , toe
    # op , toe
    ["tegen", "op"],
    ["tegen", "in"],
    # met , mee
    # op , na
    # bij , na
    # bij , af
]

circumpositionwordsdict = {f"{vz}{az}": (
    vz, az) for (vz, az) in circumpositions}


def metmeetottoe(prep: str) -> str:
    if prep == "met":
        newprep = "mee"
    elif prep == "tot":
        newprep = "toe"
    else:
        newprep = prep
    return newprep


def mkpronadvs(prep: str, postp: Optional[str] = None) -> List[str]:
    if prep == "met":
        newprep = "mee"
    elif prep == "tot":
        newprep = "toe"
    else:
        newprep = prep
    if postp is None:
        if newprep in Radpositions:
            results = [f"{rpronoun}{newprep}" for rpronoun in Rpronouns]
        else:
            results = []
    else:
        if [newprep, postp] in circumpositions:
            results = [f"{rpronoun}{newprep}{postp}" for rpronoun in Rpronouns]
        else:
            results = []
    return results


PronAdpositionTuple = Optional[Tuple[str, Tuple[str, Optional[str]]]]


def pronadv2vz(pronadv: str, lemma=True) -> Optional[Tuple[str, Optional[str]]]:
    pronvz = pronadv2pronvz(pronadv, lemma)
    if pronvz is not None:
        (pron, vz) = pronvz
        result = vz
    else:
        result = None
    return result


def ispronadvp(node: SynTree) -> bool:
    children = [child for child in node]
    result = len(children) == 1 and ispronadv(children[0])
    return result


def ispronadv(node: SynTree) -> bool:
    if 'lemma' not in node.attrib:
        return False
    lemma = node.get('lemma')
    pronvzaztuple = pronadv2pronvz(lemma)
    if pronvzaztuple is None:
        result = False
    else:
        (pron, (vz, az)) = pronvzaztuple
        if az is None:
            result = vz in Radpositions
        else:
            result = f'{vz}{az}' in circumpositionwordsdict
    return result


def pronadv2pronvz(pronadv: str, lemma=True) -> PronAdpositionTuple:
    result: PronAdpositionTuple
    cleanpronadv = strip_accents(pronadv).lower()
    if cleanpronadv in allpronadvlemmas:
        if cleanpronadv[:4].lower() in {"daar", "hier", "waar"}:
            pron = pronadv[:4]
            result1 = pronadv[4:]
        elif cleanpronadv[:3].lower() in {"d'r"}:
            pron = pronadv[:3]
            result1 = pronadv[3:]
        elif cleanpronadv[:2].lower() in {"er", "dr"}:
            pron = pronadv[:2]
            result1 = pronadv[2:]
        else:
            pron = None
            result1 = None
        if result1 is not None and pron is not None:
            cleanresult1 = strip_accents(result1).lower()
            if cleanresult1 in circumpositionwordsdict:
                result = (pron, circumpositionwordsdict[cleanresult1])
            else:
                result = (pron, (result1, None))
            (pron, (vz, az)) = result
            cleanvz = strip_accents(vz).lower()
            if lemma:
                if cleanvz == "mee":
                    result = (pron, ("met", az))
                elif cleanvz == "toe":
                    result = (pron, ("tot", az))
                else:
                    pass
    else:
        result = None
    return result


advprons1 = set(
    rpronoun + radposition for rpronoun in Rpronouns for radposition in Radpositions
)

advprons2 = set(
    rpronoun + "".join(circumposition)
    for rpronoun in Rpronouns
    for circumposition in circumpositions
)

pronadvlemmas = advprons1.union(advprons2)

robustadvprons1 = set(
    set(
        rpronoun + radposition
        for rpronoun in robustrpronouns
        for radposition in Radpositions
    )
)
robustadvprons2 = set(
    rpronoun + "".join(circumposition)
    for rpronoun in robustrpronouns
    for circumposition in circumpositions
)

robustadvlemmas = robustadvprons1.union(robustadvprons2)
allpronadvlemmas = pronadvlemmas.union(robustadvlemmas)

junk = 0

aanvz = ("aan", None)
opafvz = ("op", "af")
meevz = ("met", None)
toevz = ("tot", None)


def test():
    testadvprons = [
        ("eraan", aanvz),
        ("hieraan", aanvz),
        ("waaraan", aanvz),
        ("daaraan", aanvz),
        ("d'raan", aanvz),
        ("draan", aanvz),
        ("ermee", meevz),
        ("hiermee", meevz),
        ("waarmee", meevz),
        ("daarmee", meevz),
        ("d'rmee", meevz),
        ("drmee", meevz),
        ("ertoe", toevz),
        ("hiertoe", toevz),
        ("waartoe", toevz),
        ("daartoe", toevz),
        ("d'rtoe", toevz),
        ("drtoe", toevz),
        ("eropaf", opafvz),
        ("hieropaf", opafvz),
        ("waaropaf", opafvz),
        ("daaropaf", opafvz),
        ("d'ropaf", opafvz),
        ("dropaf", opafvz),
        ("Wáártoe", toevz)
    ]

    counter = 0
    for testadvpron, correct in testadvprons:
        counter += 1
        result = pronadv2vz(testadvpron)
        if result != correct:
            print(f"NO:{testadvpron}: {result} != {correct}")
    print(f'{counter} examples tested')


def rvz(vzlemma: str) -> List[str]:
    if vzlemma == 'met':
        newvzlemma = 'mee'
    elif vzlemma == 'tot':
        newvzlemma = 'toe'
    else:
        newvzlemma = vzlemma

    result = [f'{rpronoun}{newvzlemma}' for rpronoun in fixedrpronouns]
    return result


if __name__ == "__main__":
    test()
