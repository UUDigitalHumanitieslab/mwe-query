from .mwe_annotate import annotate
from .mwemeta import mwemetaheader, metatoparsemetsv3
from sastadev.xlsx import mkworkbook
from sastadev.alpinoparsing import parse
from .canonicalform import expandfull
from typing import List, Tuple


def select(sents: List[Tuple[int, str]], uttid=None):
    if uttid is not None:
        results = [(i, sent) for (i, sent) in sents if i == uttid]
    else:
        results = sents
    return results


def tryannotate():
    sentences = []
    stophere = 0  # with 0 it will do all, with a positive value n it will stop after n examples
    sentences += [
        (1, "hij poetste de plaat"),
        (2, "hij poetste de mooie plaat"),
        # (3, 'hij poetste, maar de plaat werd niet mooi') completely wrong parse so MEQ
        (3, "hij poetste, hoewel de plaat niet mooier werd"),
    ]
    sentences += [
        (4, "Daar kraait geen haan naar"),
        (5, "Hier heeft geen haan naar gekraaid"),
        (6, "geen haan kraaide daarnaar"),
        (7, "geen haan kraaide ernaar dat hij niet kwam"),
        (8, "geen haan kraaide er naar dat hij niet kwam"),
        (9, "er is geen haan die daar naar kraait"),
    ]
    sentences += [
        (10, "Een varkentje dat even vlug gewassen moest worden door PSV Eindhoven .")
    ]
    sentences += [(11, "als puntje bij paaltje komt laat hij het afweten")]
    sentences += [(12, "iemand zal als de kippen er bij zijn")]
    sentences += [
        (13, "iemand zal een tik van de molen krijgen"),
        (14, "iemand zal iemand tegenover zich krijgen"),
    ]
    sentences += [(15, "De buurman van An houdt de boeken van Piet die zij houdt")]
    sentences += [
        (16, "hij zal  als de kippen er bij zijn"),
        (17, "hij zal er als de kippen bij zijn"),
    ]
    sentences += [
        (18, "hij legde de boeken neer"),
        (19, "hij heeft de boeken neergelegd"),
    ]
    sentences += [
        (20, "Er kraaide geen haan naar dat Saab de boeken neer moest leggen")
    ]
    sentences += [(21, "Hij poetste de plaat toen Saab de boeken neer moest leggen")]
    sentences += [(22, "hij poetste de plaat toen hij ziek was")]
    sentences += [(23, "hij poetste de plaat")]
    sentences += [(24, "iemand zal iemand tegenover zich krijgen")]
    sentences += [(25, "Waarvan houdt hij niet?")]
    sentences += [(26, "Hij houdt van boeken")]
    sentences += [(27, "Hij houdt er niet van")]
    sentences += [(28, "Hij houdt hiervan")]
    sentences += [(29, "Hij heeft toch wel iets")]
    sentences += [(30, "iemand zal onder ede staan")]
    sentences += [(31, "iemand zal aan komen wippen")]
    sentences += [(32, "iets zal hand over hand toenemen")]
    sentences += [(33, "Hij is een klein beetje aangekomen")]
    sentences += [(34, "Hij heeft een klein beetje gegeten")]
    sentences += [(35, "iemand zal gebruik van de weg maken")]
    sentences += [(36, "Het verband in Jan lag met hem op straat")]
    sentences += [(37, "Op voorstel hiervan lag er een voorstel")]
    sentences += [(38, "Er kwamen veel boeken in omloop")]
    sentences += [(39, "Niemand denkt dat die vlieger opgaat")]
    sentences += [(40, "Er werden pogingen gedaan om dat probleem op te lossen")]
    sentences += [(41, "onder leiding van Jan")]
    sentences += [(42, "hij nam het in gebruik")]
    sentences += [(43, "hij ziet het zitten")]

    fullmwemetalist = []
    counter = 0
    selectedsentences = select(sentences, uttid=6)
    for id, sentence in selectedsentences:
        counter += 1
        print(f"annotating {id}: {sentence}...")
        if counter == stophere:
            break
        tree = parse(sentence)
        expandedtree = expandfull(tree)
        mwemetalist, _, _ = annotate(expandedtree, id)

        fullmwemetalist += mwemetalist
        ptsv3 = metatoparsemetsv3(sentence, mwemetalist)
        with open(f"./ptsv3/{id:03}.ptsv3", "w", encoding="utf8") as outfile:
            print(ptsv3, file=outfile)

    fullrowlist = [mwemeta.torow() for mwemeta in fullmwemetalist]
    wb = mkworkbook(
        "MWEmetadata_tryannotate.xlsx",
        [mwemetaheader],
        fullrowlist,
        freeze_panes=(1, 0),
    )
    wb.close()


if __name__ == "__main__":
    tryannotate()
