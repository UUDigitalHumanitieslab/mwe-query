from typing import List, Tuple
from mwe_query.canonicalform import preprocess_MWE, expandcanonicalform


def select(iexamples, uttid=None) -> List[Tuple[int, str]]:
    if uttid is None:
        return iexamples
    else:
        result = []
        for i, example in iexamples:
            if i == uttid:
                return [(i, example)]
    return result


iexamples = [
    (1, "iemand zal 0een L:poging DO:doen"),
    (2, "iemand zal L:[in de war] BE:zijn"),
    (3, "iemand zal ^niet voor de poes zijn"),
    (4, "iemand zal M:[in de war] BC:raken"),
    (5, "iemand zal M:[in de war] ST:blijven"),
    (6, "iemand zal iemand M:[in de war] CBC:maken"),
    (7, "iemand zal iemand M:[in de war] CST:houden"),
    (8, "iemand zal iemand M:[in de war] GT:krijgen"),
    (9, "iemand zal de M:dans L:ontspringen"),
    (10, "iemand zal 0dat M:varken M:wassen"),
    (11, "iemand zal ^geen L:[flauw idee] OIA:van iets BE:hebben"),
    (12, "iemand zal 0een L:oogje CIA:op iemand | iets BE:hebben"),
    (13, "iemand zal L:[onder *druk] BE:staan")
]

selectediexamples = select(iexamples, uttid=13)
for i, rawexample in selectediexamples:
    examples = expandcanonicalform(rawexample)
    for example in examples:
        wordanns = preprocess_MWE(example)
        print(f"{i}: {example}")
        for word, ann in wordanns:
            print(f"{word}: {ann}")
