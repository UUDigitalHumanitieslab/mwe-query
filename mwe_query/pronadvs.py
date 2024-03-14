"""
The module proadvs generates a list of pronominal adverb lemmas (pronadvlemmas)
and provides a function to create pronominal adverb lemmas (strings)
"""

from typing import List, Optional, Tuple

Rpronouns = ["er", "hier", "daar", "waar"]
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

circumpositionwordsdict = {f"{vz}{az}": (vz, az) for (vz, az) in circumpositions}


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


def pronadv2vz(pronadv: str) -> Optional[Tuple[str, Optional[str]]]:
    result: Optional[Tuple[str, Optional[str]]]
    if pronadv in allpronadvlemmas:
        if pronadv[:4] in {"daar", "hier", "waar"}:
            result1 = pronadv[4:]
        elif pronadv[:3] in {"d'r"}:
            result1 = pronadv[3:]
        elif pronadv[:2] in {"er", "dr"}:
            result1 = pronadv[2:]
        else:
            result1 = None
        if result1 is not None:
            if result1 in circumpositionwordsdict:
                result = circumpositionwordsdict[result1]
            else:
                result = (result1, None)
    else:
        result = None
    (vz, az) = result
    if vz == "mee":
        result = ("met", az)
    elif vz == "toe":
        result = ("tot", az)
    else:
        pass
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
    ]

    for testadvpron, correct in testadvprons:
        result = pronadv2vz(testadvpron)
        if result != correct:
            print(f"NO:{testadvpron}: {result} != {correct}")


if __name__ == "__main__":
    test()
