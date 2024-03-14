from sastadev.alpinoparsing import parse
from sastadev.treebankfunctions import showtree
from lxml import etree
from .canonicalform import generatequeries, expandfull

debug = False

geenhaankraaien = (
    "0geen *haan zal naar iets kraaien",
    [
        "maar daar kraait geen haan naar maar als het er drieduizend zijn of meer staat belgie op "
        "zen kop kweet niet of da verschil even groot is hoor",
        "Daar kraait geen haan naar",
        "Hier heeft geen haan naar gekraaid",
        "geen haan kraaide daarnaar",
        "geen haan kraaide ernaar dat hij niet kwam",
        "geen haan kraaide er naar dat hij niet kwam",
        "er is geen haan die daar naar kraait",
        "Weinig hanen die daarnaar kraaien .",
        "Weinig hanen die ernaar kraaiden .",
        "Oost-Europese au pairs komen als toerist naar Nederland en "
        "volgens Ales kraait er geen haan naar dat ze stiekem werken .",
    ],
)

invoorietszijn = (
    "iemand zal in voor iets zijn",
    ["iemand zal in voor iets zijn", "hij zal daar voor in zijn"],
)
voorietsinzijn = (
    "iemand zal voor iets in zijn",
    [
        "iemand zal voor iets in zijn",
        "hij zal daar voor in zijn",
        "hij zal daarvoor in zijn",
        "hij zal in voor een feest zijn",
        "hij zal in zijn voor een feest",
    ],
)

puntjebijpaaltje = (
    "als puntje bij paaltje +komt",
    ["als puntje bij paaltje komt", "als puntje bij paaltje kwam"],
)

zalwel = ("dd:[dat] +zal wel", ["het zal wel", "dat zal wel"])

varkentjewassen = (
    "iemand zal 0dit +*varkentje wassen",
    ["Een varkentje dat even vlug gewassen moest worden door PSV Eindhoven ."],
)

ingevalvaniets = (
    "in geval van iets",
    ["in geval van ongelukken", "in geval hiervan", "in geval hier van"],
)

houdenvan = (
    "iemand zal van iemand|iets houden",
    [
        "hij houdt van voetbal",
        "Hij houdt er niet van",
        "Hij houdt ervan",
        "Hij houdt daarvan",
        "Hij houdt ervan om te schaken",
        "hij houdt er van om te schaken",
        "hij houdt er niet van om te schaken",
    ],
)
zichschamen = (
    "iemand zal zich schamen",
    [
        "ik schaam me",
        "jij schaamt je",
        "hij schaamt zich",
        "zij schaamt zich",
        "wij schamen ons",
        "jullie schamen je",
        "zij schamen zich",
    ],
)

zichzelfzijn = (
    "iemand zal zichzelf zijn",
    [
        "ik ben mijzelf",
        "jij bent jezelf",
        "hij is zichzelf",
        "zij is zichzelf",
        "wij zijn onszelf",
        "jullie zijn jezelf",
        "zij zijn zichzelf",
    ],
)

deplaatpoetsen = (
    "iemand zal de plaat poetsen",
    [
        "hij poetste de plaat",
        "hij poetste gisteren de plaat",
        "hij poetste de plaat toen hij ziek was",
    ],
)

ietshebben = ("iemand|iets zal =iets hebben", ["hij heeft toch wel iets"])

tukhebben = (
    "iemand zal iemand tuk hebben",
    ["hij heeft mij tuk", "iemand zal iemand tuk hebben"],
)

liegenbarsten = (
    "iemand zal liegen dat hij +barst",
    [
        "ik lieg dat ik barst",
        "jij liegt dat je barst",
        "hij liegt dat ie barst",
        "wij liegen dat we barsten",
        "jullie liegen dat jullie barsten",
        "zij liegen dat ze barsten ",
        "zij logen dat ze barstten",
    ],
)
vrolijkeFrans = [
    ("0een vrolijke Frans"),
    [
        "een vrolijk Fransje",
        "dit vrolijke Fransje",
        "vrolijke Fransen",
        "vrolijke Fransjes",
        "een vrolijke Frans",
    ],
]


def select(mweutts, utt=None):
    if utt is None:
        result = mweutts
    else:
        result = (mweutts[0], [mweutts[1][utt]])
    return result


def getparses(utterances):
    uttparses = []
    for utterance in utterances:
        uttparse = parse(utterance)
        uttparses.append(uttparse)
    return uttparses


def trysomemwes():
    mwe, utterances = select(invoorietszijn)
    mwe, utterances = select(puntjebijpaaltje)
    mwe, utterances = select(zalwel)
    mwe, utterances = select(varkentjewassen)
    mwe, utterances = select(voorietsinzijn)  # hier zitten missers van MWEQ bij
    mwe, utterances = select(ingevalvaniets)
    mwe, utterances = select(geenhaankraaien)
    mwe, utterances = select(houdenvan)
    mwe, utterances = select(zichschamen)
    mwe, utterances = select(zichzelfzijn)
    mwe, utterances = select(deplaatpoetsen)
    mwe, utterances = select(houdenvan)
    mwe, utterances = select(ietshebben)
    mwe, utterances = select(geenhaankraaien)
    mwe, utterances = select(tukhebben)
    mwe, utterances = select(liegenbarsten)
    mwe, utterances = select(vrolijkeFrans)
    mwequeries = generatequeries(mwe)
    labeledmwequeries = (
        ("MWEQ", mwequeries[0]),
        ("NMQ", mwequeries[1]),
        ("MLQ", mwequeries[2]),
    )
    uttparses = getparses(utterances)
    for utterance, uttparse in zip(utterances, uttparses):
        print(f"{utterance}:")
        expandeduttparse = expandfull(uttparse)
        showparses = True
        if showparses:
            showtree(expandeduttparse, "expandeduttparse")
        for label, mwequery in labeledmwequeries:
            results = expandeduttparse.xpath(mwequery)
            if debug:
                print("Found hits:")
                for result in results:
                    etree.dump(result)
            print(f"{label}: {len(results)}")


if __name__ == "__main__":
    trysomemwes()
