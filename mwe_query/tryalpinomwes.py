from sastadev.alpinoparsing import parse
from .getalpinomwes import getalpinomwes

tab = "\t"

isentences = [(1, "dat doet zich vaak voor")]
isentences += [(2, "hij lijkt wel op mijn vader")]
isentences += [(3, "hij heeft zich altijd aan zijn vriend op kunnen trekken")]
isentences += [(4, "hij liet dat aan hen zien")]
isentences += [
    (
        5,
        "Maar we mogen de problemen waar burgers mee te maken  hebben niet onderschatten .",
    )
]
isentences += [(6, "Het presidentiële bevelschrift werd in de wind  geslagen.")]
isentences += [(7, "Hij schaamt zich")]
isentences += [(8, "Wij hebben daar niets mee te maken")]
isentences += [(9, "Hij moest verstek laten gaan")]
isentences += [(10, "de brug over de rivier heen")]
isentences += [(11, "Commissaris Nielson is er vandaag naar toe .")]
isentences += [(12, "Hij zal het af laten weten")]
isentences += [(13, "Hij zal het laten afweten")]
isentences += [(14, "Hij houdt van Marie")]
isentences += [(15, "Hij zal argumenten kracht bij zetten")]
isentences += [(16, "Hij schaamt zich voor zijn gedrag")]
isentences += [
    (
        17,
        "De meesten zouden zich nu vermoedelijk schamen voor wat zij mede hebben aangericht .",
    )
]
isentences += [
    (
        18,
        "Het kenmerkt zich taalkundig gezien door o.m. leenwoorden uit het Frans en door sommige klanken die onder Franse invloed staan .",
    )
]
isentences += [(19, "Hij legde de pen neer")]
isentences = [(20, "Beide stonden ze aan het hoofd van een paarsgroene coalitie")]
if __name__ == "__main__":
    for sentenceid, sentence in isentences:
        stree = parse(sentence)
        if stree is not None:
            mwemetas = getalpinomwes(stree, sentenceid=sentenceid)
            for mwemeta in mwemetas:
                fullrow = mwemeta.torow()
                print(tab.join(fullrow))
        else:
            print(f"No parse found for {sentenceid}: {sentence}")
